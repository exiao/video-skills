# Video skills

A collection of agent skills for making videos, from concept to finished edit. Each directory under `skills/` contains a `SKILL.md` and its supporting references and tools.

- **animation-creator** — animation and motion graphics with Claude and local renderers.
- **video-direction**, **video-script**, **storyboards** — treatments, scripts, shots and illustrated boards.
- **video-editor**, **sound-storytelling**, **thumbnail** — editing, sound and packaging.
- **reference-style-video**, **image-to-video** — reference analysis and image animation.
- **camera-3d-captions**, **vox-explainer** — specialized caption and explainer workflows.

## Use

Clone the repository and copy or symlink the desired skill directories into your agent's skills directory (for Codex, `~/.codex/skills/`). Install the collection together to retain cross-references between included skills. For example:

```sh
git clone https://github.com/exiao/video-skills.git
mkdir -p ~/.codex/skills
cp -R video-skills/skills/. ~/.codex/skills/
```

Check for existing skills before copying: this command can overwrite files with the same names. Restart or refresh your agent's skill discovery if needed.

Some workflows refer to external skills, services, CLIs, local assets, or paid providers that are not included. The original instructions contain personal preferences and examples that may need adapting to your environment. Reference screenshots are omitted; relevant written descriptions remain. The p5 helper's dependencies are installed separately using its included setup script and package lock. Review any script before running it.
