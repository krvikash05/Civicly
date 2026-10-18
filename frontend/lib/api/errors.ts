import type { ApiModels } from '../generated/models';
export class ApiError extends Error {
  readonly code: string;
  readonly status: number;
  readonly requestId: string | null;
  readonly details: ApiModels['ErrorDetails'];
  readonly uncertain: boolean;
  constructor(code:string,status=0,requestId:string|null=null,details:ApiModels['ErrorDetails']={}) {
    super(errorMessage(code));this.name='ApiError';this.code=code;this.status=status;this.requestId=requestId;this.details=details;
    this.uncertain=code==='RECOVERY_REQUIRED'||code==='WRITE_OUTCOME_UNKNOWN';
  }
}
export function errorMessage(code: string): string {
  const messages: Record<string,string> = {
    DEMO_UNAVAILABLE:'The demo connection is not available yet. Please ask the presenter to configure it.',
    EXTERNAL_UNAVAILABLE:'The backend connection is unavailable. Please ask the presenter to check it.',
    GRAPH_UNAVAILABLE:'The graph service is unavailable. Please ask the presenter to check it.',
    UNAUTHORIZED:'Your demo session has ended. Reconnect to continue.',
    PERMISSION_DENIED:'This demo identity cannot perform that action.',
    VALIDATION_ERROR:'The request does not match the current API contract.',
    CLIENT_VALIDATION:'The request does not match the current API contract.',
    CONTRACT_MISMATCH:'The response does not match the reviewed API contract. Please ask the presenter to check compatibility.',
    SELECTION_MISMATCH:'The selected incident or investigation does not match the active filter or case.',
    RECOVERY_REQUIRED:'This action requires operator reconciliation. Do not submit it again with a new request key.',
    WRITE_OUTCOME_UNKNOWN:'The action may have reached the server. Preserve the original request key and ask the operator to check it.',
    CONFLICT:'The resource or request has changed. Review the current version before continuing.',
    DEPENDENCY_BLOCKED:'Required evidence, approval or a dependency is not yet satisfied.',
    READ_CAPACITY:'The result exceeds the supported bounds. Narrow the request.',
    NOT_FOUND:'The requested resource is unavailable.',
    NETWORK_ERROR:'The connection was interrupted. Reconnect when the service is available.',
    REQUEST_CANCELLED:'The request was cancelled.',
    SESSION_CHANGED:'The demo session changed while this request was in progress.',
  };
  return messages[code] ?? 'The request could not be completed. Please ask the presenter to check it.';
}
