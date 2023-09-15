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

- Tag format: `minecraft-installer-bullseye-17`, `minecraft-runtime-${OS}-${JDK_VER}-${MCDR_VER}`
- OS: `bullseye`, `slim-bullseye`
- JDK_VER: `8`, `17`
- MCDR_VER: `latest`, `2.10`

