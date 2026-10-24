/// <reference types="vite/client" />
interface ImportMetaEnv {
  readonly VITE_USE_MOCKS: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
}

