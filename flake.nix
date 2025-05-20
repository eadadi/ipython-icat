{
  description = "dev shell with uv & claude code";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }: let
    system = "x86_64-linux";
    pkgs   = import nixpkgs {
      inherit system; config.allowUnfree = true;
    };
  in {
    devShell.${system} = pkgs.mkShell {
      buildInputs = with pkgs; [
        nodejs_20
        python312Full
        uv
      ];

      shellHook = ''
        export LD_LIBRARY_PATH=${
          pkgs.lib.makeLibraryPath [
            pkgs.zlib
            pkgs.stdenv.cc.cc
          ]
        }:$LD_LIBRARY_PATH
        export NPM_CONFIG_PREFIX="$HOME/.npm-global"
        export PATH="$HOME/.npm-global/bin:$PATH"

        if [ ! -f "$HOME/.npm-global/bin/claude" ]; then
          npm install -g @anthropic-ai/claude-code
        fi
      '';
    };
  };
}
