import type { ReactNode } from 'react';
import site from '../content/site.json';
import './globals.css';

export const metadata = { title: site.title };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
