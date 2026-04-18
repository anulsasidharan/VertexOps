import React, {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from "react";

import { buildAuthHeaders, type AuthHeaders } from "@/api/client";

export type AuthMode = "none" | "jwt" | "api_key";

type AuthSessionState = {
  mode: AuthMode;
  jwt: string | null;
  apiKey: string | null;
};

type AuthSessionContextValue = AuthSessionState & {
  setJwtSession: (token: string) => void;
  setApiKeySession: (key: string) => void;
  clearSession: () => void;
  getAuthHeaders: () => AuthHeaders;
  isAuthenticated: boolean;
};

const STORAGE_JWT = "vertexops_jwt";
const STORAGE_KEY = "vertexops_api_key";
const STORAGE_MODE = "vertexops_auth_mode";

const AuthSessionContext = createContext<AuthSessionContextValue | null>(null);

function readInitial(): AuthSessionState {
  try {
    const mode = (localStorage.getItem(STORAGE_MODE) as AuthMode) || "none";
    const jwt = localStorage.getItem(STORAGE_JWT);
    const apiKey = localStorage.getItem(STORAGE_KEY);
    if (mode === "jwt" && jwt) return { mode: "jwt", jwt, apiKey: null };
    if (mode === "api_key" && apiKey) return { mode: "api_key", jwt: null, apiKey };
  } catch {
    /* private mode */
  }
  return { mode: "none", jwt: null, apiKey: null };
}

export function AuthSessionProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthSessionState>(readInitial);

  const setJwtSession = useCallback((token: string) => {
    try {
      localStorage.setItem(STORAGE_MODE, "jwt");
      localStorage.setItem(STORAGE_JWT, token);
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      /* ignore */
    }
    setState({ mode: "jwt", jwt: token, apiKey: null });
  }, []);

  const setApiKeySession = useCallback((key: string) => {
    try {
      localStorage.setItem(STORAGE_MODE, "api_key");
      localStorage.setItem(STORAGE_KEY, key);
      localStorage.removeItem(STORAGE_JWT);
    } catch {
      /* ignore */
    }
    setState({ mode: "api_key", jwt: null, apiKey: key });
  }, []);

  const clearSession = useCallback(() => {
    try {
      localStorage.removeItem(STORAGE_MODE);
      localStorage.removeItem(STORAGE_JWT);
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      /* ignore */
    }
    setState({ mode: "none", jwt: null, apiKey: null });
  }, []);

  const getAuthHeaders = useCallback(() => {
    return buildAuthHeaders(state.mode, state.jwt, state.apiKey);
  }, [state.mode, state.jwt, state.apiKey]);

  const value = useMemo<AuthSessionContextValue>(
    () => ({
      ...state,
      setJwtSession,
      setApiKeySession,
      clearSession,
      getAuthHeaders,
      isAuthenticated:
        (state.mode === "jwt" && !!state.jwt) ||
        (state.mode === "api_key" && !!state.apiKey),
    }),
    [state, setJwtSession, setApiKeySession, clearSession, getAuthHeaders]
  );

  return (
    <AuthSessionContext.Provider value={value}>{children}</AuthSessionContext.Provider>
  );
}

export function useAuthSession(): AuthSessionContextValue {
  const ctx = useContext(AuthSessionContext);
  if (!ctx) {
    throw new Error("useAuthSession must be used within AuthSessionProvider");
  }
  return ctx;
}
