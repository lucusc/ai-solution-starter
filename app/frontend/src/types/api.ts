export interface ApiErrorBody {
  code: string;
  message: string;
  request_id: string;
  details: Record<string, unknown> | null;
}

export interface ApiErrorEnvelope {
  error: ApiErrorBody;
}

export interface EasyAuthClaim {
  typ: string;
  val: string;
}

export interface EasyAuthPrincipal {
  user_id?: string;
  user_name?: string;
  identity_provider?: string;
  user_claims?: EasyAuthClaim[];
}
