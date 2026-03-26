import { AlertCircle, Inbox, Loader2 } from 'lucide-react';

import { Button } from '../button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../card';

type PageStateVariant = 'loading' | 'error' | 'empty';

interface PageStateProps {
  variant: PageStateVariant;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}

export function PageState({ variant, title, description, actionLabel, onAction }: PageStateProps) {
  const Icon =
    variant === 'loading' ? Loader2 : variant === 'error' ? AlertCircle : Inbox;

  return (
    <Card className="mx-auto max-w-2xl shadow-sm">
      <CardHeader>
        <div className="mb-3 inline-flex rounded-full bg-primary/10 p-3 text-primary">
          <Icon className={`h-5 w-5 ${variant === 'loading' ? 'animate-spin' : ''}`} />
        </div>
        <CardTitle className="text-2xl font-semibold tracking-tight">{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      {(actionLabel || onAction) && (
        <CardContent>
          <Button onClick={onAction} type="button" variant={variant === 'error' ? 'default' : 'outline'}>
            {actionLabel ?? 'Continue'}
          </Button>
        </CardContent>
      )}
    </Card>
  );
}
