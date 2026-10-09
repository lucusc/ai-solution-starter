import type { EasyAuthPrincipal } from "../types/api";

export interface Account {
  displayName: string;
  isLocal: boolean;
}

export async function getAccount(signal?: AbortSignal): Promise<Account | null> {
  try {
    const response = await fetch("/.auth/me", {
      headers: { Accept: "application/json" },
      signal,
    });
    if (!response.ok) return localAccount();
    const principals = (await response.json()) as EasyAuthPrincipal[];
    const principal = principals[0];
    if (!principal) return localAccount();
    return {
      displayName: principal.user_name || "Signed-in user",
      isLocal: false,
    };
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") throw error;
    return localAccount();
  }
}

function localAccount(): Account | null {
  const displayName = import.meta.env.VITE_LOCAL_AUTH_DISPLAY_NAME;
  return displayName ? { displayName, isLocal: true } : null;
}

export const signInUrl = "/.auth/login/aad?post_login_redirect_uri=/";
export const signOutUrl = "/.auth/logout?post_logout_redirect_uri=/";
