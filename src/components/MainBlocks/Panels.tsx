import type { PropsWithChildren } from "react";
import "./Panels.css";

type LeftPanelProps = {
  className?: string;
};

export function LeftPanel({ className, children }: PropsWithChildren<LeftPanelProps>) {
  const classes = ["leftPanel", className].filter(Boolean).join(" ");

  return (
    <div className={classes} style={{
        display: "flex",
        flexDirection: "column",
      }}>
      {children}
    </div>
  );
}
 

type RightPanelProps = {
  className?: string;
};

export function RightPanel({ className, children }: PropsWithChildren<RightPanelProps>) {
  const classes = ["rightPanel", className].filter(Boolean).join(" ");

  return (
    <div className={classes} style={{
        display: "flex",
        flexDirection: "column",
      }}>
      {children}
    </div>
  );
}
 