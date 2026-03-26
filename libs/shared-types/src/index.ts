export type ServiceDescriptor = {
  name: string;
  type: string;
  port: number;
  description: string;
};

export type ServiceHealth = {
  service: string;
  status: 'ok' | 'degraded' | 'down';
};