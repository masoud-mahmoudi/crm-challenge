import { PropsWithChildren } from 'react';

type ShellProps = PropsWithChildren<{
  eyebrow: string;
  title: string;
  subtitle: string;
}>;

export function Shell({ eyebrow, title, subtitle, children }: ShellProps) {
  return (
    <main className="shell">
      <header className="shell__hero">
        <span className="shell__eyebrow">{eyebrow}</span>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </header>
      {children}
    </main>
  );
}