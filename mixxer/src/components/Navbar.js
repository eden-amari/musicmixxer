import Link from "next/link";

export default function Navbar() {
  return (
    <nav style={{
      display: "flex",
      justifyContent: "space-between",
      padding: "16px",
      borderBottom: "1px solid #ccc"
    }}>
      <Link href="/">Mixxer</Link>

      <div style={{display: "flex", gap: "15px"}}>
        <Link href="/dashboard">Dashboard</Link>
        <Link href="/feed">Feed</Link>
        <Link href="/profile">Profile</Link>
        <Link href="/login">Login</Link>
      </div>
    </nav>
  );
}
