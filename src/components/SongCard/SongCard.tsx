import type { PropsWithChildren } from "react";
import "./SongCard.css";

type SongCardProps = {
  className?: string;
};

export function SongCard({ className, children }: PropsWithChildren<SongCardProps>) {
  const classes = ["songCard", className].filter(Boolean).join(" ");

  return (
    <div className={classes} style={{
        display: "flex",
        flexDirection: "column",
      }}>
      {children}

    
    </div>
  );
}
 