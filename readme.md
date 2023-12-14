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
- Runtime tag: `minecraft-runtime-${OS}-${JDK_VER}-${MCDR_VER}`
  - OS: `jammy`, `bullseye`, `slim-bullseye`
  - JDK_VER: `8`, `11`, `17`, `21`
  - MCDR_VER: `latest`, `2.12`, `2.11`, `2.10`
  - Examples:
    - `fallenbreath/pterodactyl-yolks:minecraft-runtime-jammy-8-latest`
    - `fallenbreath/pterodactyl-yolks:minecraft-runtime-jammy-17-latest`
    - `fallenbreath/pterodactyl-yolks:minecraft-runtime-slim-bullseye-21-2.12`
  - Notes:
    - OS `jammy` is based on [eclipse-temurin](https://hub.docker.com/_/eclipse-temurin) image
    - OS `bullseye`, `slim-bullseye` are based on [openjdk](https://hub.docker.com/_/openjdk) image, and are [deprecated](https://github.com/docker-library/openjdk/issues/505)
