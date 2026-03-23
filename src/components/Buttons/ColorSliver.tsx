type colorSliverProps = {
  className?: string;
};
export function ColorSliver({ className }: colorSliverProps) {
  const classes = ["colorSliver", className].filter(Boolean).join(" ");

  return (
    <div className={classes}>
    </div>
  );
}

export default ColorSliver;