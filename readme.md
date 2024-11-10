Image and eggs for my pterodactyl panel

## `eggs`: Storage for egg sources

- `eggs/minecraft`: eggs for Minecraft with MCDR
- `eggs/tools`: eggs for random tools

## `yolks`: Storage for images

DockerHub: https://hub.docker.com/r/fallenbreath/pterodactyl-yolks

Overall tag format: `${category}-${type}-${args}`, where `type` can be `installer` or `runtime`

### general

`yolks/general`: images for general applications

- Tag format: `general-installer-${OS}`, `general-runtime-${OS}`
- OS: `alpine`, `debian` (bullseye-slim)

### minecraft

`yolks/minecraft`: images for Minecraft with MCDR

- Installer tag: `minecraft-installer-bullseye-17`, only this one
- Runtime tag: `minecraft-runtime-${JDK_VER}-${MCDR_VER}`
  - JDK_VER: `8`, `11`, `17`, `21`
  - MCDR_VER: `latest`, `2.13`, `2.12`
  - Examples:
    - `fallenbreath/pterodactyl-yolks:minecraft-runtime-21-latest`
    - `fallenbreath/pterodactyl-yolks:minecraft-runtime-8-2.12`
  - Notes:
    - For `latest` MCDR, you can also use the shortcut image names that omit the os and mcdr parts:
      - `fallenbreath/pterodactyl-yolks:minecraft-runtime-8`
      - `fallenbreath/pterodactyl-yolks:minecraft-runtime-17`
