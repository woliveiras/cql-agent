export interface ChatMessageRequest {
  message: string;
  session_id?: string;
  use_rag?: boolean;
  use_web_search?: boolean;
}

export interface ChatMessageResponse {
  response: string;
  session_id: string;
  state: string;
}

export interface ApiError {
  detail: string;
  status: number;
}
