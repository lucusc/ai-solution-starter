/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_LOCAL_AUTH_DISPLAY_NAME?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
