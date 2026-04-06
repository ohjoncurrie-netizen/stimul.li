export type DifficultyLevel = "beginner" | "intermediate" | "advanced";
export type StimulusType = "Fact" | "Concept" | "Quiz";

export interface ProcessingRequest {
  long_form_text: string;
  desired_card_count: number;
  difficulty_level: DifficultyLevel;
}

export interface StimulusCard {
  prompt: string;
  insight: string;
}

export interface Stimulus {
  type: StimulusType;
  title: string;
  content_body: string;
}

export interface SubscriptionRequest {
  success_url: string;
  cancel_url: string;
}

export interface SubscriptionResponse {
  checkout_session_id: string;
  checkout_url: string;
}

export interface HealthResponse {
  status: string;
}

export interface RetryConfig {
  maxRetries?: number;
  initialDelayMs?: number;
  maxDelayMs?: number;
}

export interface StimuliClientOptions {
  baseUrl: string;
  apiKey?: string;
  timeoutMs?: number;
  retries?: RetryConfig;
  fetchFn?: typeof fetch;
}

export class StimuliApiError extends Error {
  public readonly statusCode: number;
  public readonly requestId?: string;
  public readonly responseBody?: unknown;

  constructor(message: string, statusCode: number, requestId?: string, responseBody?: unknown) {
    super(message);
    this.name = "StimuliApiError";
    this.statusCode = statusCode;
    this.requestId = requestId;
    this.responseBody = responseBody;
  }
}

/**
 * Class-based SDK for the stimul.li API.
 *
 * Features:
 * - Typed request/response contracts
 * - Automatic retries for transient failures
 * - Request timeouts via AbortController
 * - Clean error objects that expose HTTP status and request ID
 */
export class StimuliClient {
  private readonly baseUrl: string;
  private readonly apiKey?: string;
  private readonly timeoutMs: number;
  private readonly maxRetries: number;
  private readonly initialDelayMs: number;
  private readonly maxDelayMs: number;
  private readonly fetchFn: typeof fetch;

  constructor(options: StimuliClientOptions) {
    this.baseUrl = options.baseUrl.replace(/\/+$/, "");
    this.apiKey = options.apiKey;
    this.timeoutMs = options.timeoutMs ?? 15_000;
    this.maxRetries = options.retries?.maxRetries ?? 2;
    this.initialDelayMs = options.retries?.initialDelayMs ?? 300;
    this.maxDelayMs = options.retries?.maxDelayMs ?? 2_000;
    this.fetchFn = options.fetchFn ?? fetch;
  }

  /**
   * Verify the API is reachable.
   */
  async health(): Promise<HealthResponse> {
    return this.request<HealthResponse>("/health", { method: "GET" });
  }

  /**
   * Create flashcards from long-form text using the `/flash` endpoint.
   */
  async createFlashcards(payload: ProcessingRequest): Promise<StimulusCard[]> {
    return this.request<StimulusCard[]>("/flash", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  }

  /**
   * Create a Stripe Checkout Session for the current customer.
   */
  async createSubscription(payload: SubscriptionRequest): Promise<SubscriptionResponse> {
    return this.request<SubscriptionResponse>("/create-subscription", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  }

  /**
   * Generate typed Stimuli objects.
   *
   * This assumes the API exposes a `/stimuli` endpoint that returns:
   * [{ type, title, content_body }]
   */
  async generateStimuli(payload: { raw_text: string }): Promise<Stimulus[]> {
    return this.request<Stimulus[]>("/stimuli", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  }

  private async request<T>(path: string, init: RequestInit): Promise<T> {
    const headers = new Headers(init.headers ?? {});
    headers.set("Accept", "application/json");

    if (init.body) {
      headers.set("Content-Type", "application/json");
    }

    if (this.apiKey) {
      headers.set("X-API-Key", this.apiKey);
    }

    let attempt = 0;
    let delayMs = this.initialDelayMs;
    let lastError: unknown;

    while (attempt <= this.maxRetries) {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), this.timeoutMs);

      try {
        const response = await this.fetchFn(`${this.baseUrl}${path}`, {
          ...init,
          headers,
          signal: controller.signal
        });

        clearTimeout(timeout);

        if (response.ok) {
          if (response.status === 204) {
            return undefined as T;
          }

          return (await response.json()) as T;
        }

        const responseBody = await this.safeJson(response);
        const error = new StimuliApiError(
          `Request failed with status ${response.status}`,
          response.status,
          response.headers.get("X-Request-ID") ?? undefined,
          responseBody
        );

        if (!this.shouldRetry(response.status, attempt)) {
          throw error;
        }

        lastError = error;
      } catch (error) {
        clearTimeout(timeout);

        if (!this.shouldRetryNetworkError(error, attempt)) {
          throw error;
        }

        lastError = error;
      }

      attempt += 1;
      await this.sleep(delayMs);
      delayMs = Math.min(delayMs * 2, this.maxDelayMs);
    }

    throw lastError instanceof Error ? lastError : new Error("Request failed");
  }

  private shouldRetry(statusCode: number, attempt: number): boolean {
    if (attempt >= this.maxRetries) {
      return false;
    }

    return statusCode === 408 || statusCode === 429 || statusCode >= 500;
  }

  private shouldRetryNetworkError(error: unknown, attempt: number): boolean {
    if (attempt >= this.maxRetries) {
      return false;
    }

    return error instanceof Error;
  }

  private async safeJson(response: Response): Promise<unknown> {
    try {
      return await response.json();
    } catch {
      return await response.text();
    }
  }

  private async sleep(delayMs: number): Promise<void> {
    await new Promise((resolve) => setTimeout(resolve, delayMs));
  }
}
