#!/usr/bin/env python3
"""Convert WebVTT cues into full JSON and a timestamped research transcript."""
import argparse
import html
import json
from pathlib import Path
import re
import sys

STAMP = r'(?:\d{2,}:)?\d{2}:\d{2}\.\d{3}'
TIMING = re.compile(rf'^({STAMP})\s+-->\s+({STAMP})(?:\s+.*)?$')


def seconds(stamp):
    parts = stamp.split(':')
    return sum(float(part) * 60 ** i for i, part in enumerate(reversed(parts)))


def parse_vtt(source):
    source = source.lstrip('\ufeff').replace('\r\n', '\n').replace('\r', '\n')
    if not re.match(r'^WEBVTT(?:[ \t\n]|$)', source):
        raise ValueError('Expected a WebVTT file beginning with WEBVTT')
    cues = []
    for block in re.split(r'\n[ \t]*\n', source):
        lines = block.splitlines()
        if not lines or re.match(r'^(WEBVTT|NOTE|STYLE|REGION)(?:\s|$)', lines[0]):
            continue
        index = 0 if '-->' in lines[0] else 1
        if index >= len(lines) or not TIMING.fullmatch(lines[index]):
            raise ValueError('Invalid cue timing: ' + lines[0][:100])
        match = TIMING.fullmatch(lines[index])
        start, end = match.groups()
        if seconds(end) < seconds(start):
            raise ValueError('Cue ends before it starts: ' + start)
        raw = '\n'.join(lines[index + 1:])
        # Keep explicit voice annotations; never invent speaker labels.
        marked = re.sub(r'<v(?:\.[^\s>]*)?\s+([^>]+)>', r'\1: ', raw)
        words = []
        previous_line = []
        previous_timed = False
        for line in marked.splitlines():
            current = html.unescape(re.sub(r'<[^>]*>', '', line)).split()
            fresh = current
            if previous_timed:
                for count in range(min(len(previous_line), len(current)), 1, -1):
                    if previous_line[-count:] == current[:count]:
                        fresh = current[count:]
                        break
            words.extend(fresh)
            previous_line = current
            previous_timed = bool(re.search(rf'<{STAMP}>', line))
        text = ' '.join(words)
        cues.append(dict(start=start, end=end, text=text, raw_text=raw))
    if not cues:
        raise ValueError('No caption cues found')
    return cues


def transcript(cues):
    rows = []
    previous = None
    for cue in cues:
        words = cue['text'].split()
        fresh = words
        if previous and seconds(cue['start']) <= seconds(previous['end']):
            old = previous['text'].split()
            for count in range(min(len(old), len(words)), 0, -1):
                # At a touching boundary, only remove a multiword prefix
                # when new words follow it; keep complete repeated utterances.
                touching = seconds(cue['start']) == seconds(previous['end'])
                if touching and (count < 2 or count == len(words)):
                    continue
                if old[-count:] == words[:count]:
                    fresh = words[count:]
                    break
        if fresh:
            rows.append(f"[{cue['start']} --> {cue['end']}] {' '.join(fresh)}")
        previous = cue
    return '\n'.join(rows) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output-prefix', required=True, type=Path)
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    try:
        cues = parse_vtt(args.input.read_text(encoding='utf-8-sig'))
        outputs = [Path(str(args.output_prefix) + suffix) for suffix in ('.json', '.txt')]
        if args.input.resolve() in [path.resolve() for path in outputs]:
            raise ValueError('Output must not replace the source')
        if not args.force and any(path.exists() for path in outputs):
            raise ValueError('Output exists; choose another prefix or use --force')
        rendered = transcript(cues)
        payload = dict(source=str(args.input.resolve()), cue_count=len(cues), cues=cues)
        contents = [json.dumps(payload, ensure_ascii=False, indent=2) + '\n', rendered]
        for path, content in zip(outputs, contents):
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('w' if args.force else 'x', encoding='utf-8') as stream:
                stream.write(content)
        print(json.dumps(dict(cues=len(cues), characters=len(rendered), outputs=list(map(str, outputs)))))
    except (OSError, ValueError) as error:
        print(f'clean_vtt: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
