import * as React from 'react';

type ContentLayoutProps = {
  title: string;
  children: React.ReactNode;
};

/**
 * Standard page wrapper used by every app route.
 * Renders a heading and wraps content in a consistent container.
 */
export function ContentLayout({ title, children }: ContentLayoutProps) {
  return (
    <div className="content-layout">
      <h1 className="content-layout__title">{title}</h1>
      <div className="content-layout__body">{children}</div>
    </div>
  );
}
