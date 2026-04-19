"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useAuth } from "@/components/providers/AuthProvider";
import mxrLogo from "/src/assets/images/mxr.png";
import { ColorThemeButton } from "@/components/Buttons/Buttons";
import Image from "next/image";
export default function SignInPage() {
	const router = useRouter();
	const { signIn } = useAuth();
	const [form, setForm] = useState({
		email: "",
		password: "",
		remember_me: true,
	});
	const [error, setError] = useState<string | null>(null);
	const [isSubmitting, setIsSubmitting] = useState(false);

	return (
		<main className="auth-shell">

			<form
				className="auth-card"
				onSubmit={(event) => {
					event.preventDefault();
					setIsSubmitting(true);
					setError(null);
					void signIn(form)
						.then(() => router.push("/account/dashboard"))
						.catch((nextError) => {
							setError(
								nextError instanceof Error ? nextError.message : "Unable to sign in.",
							);
						})
						.finally(() => setIsSubmitting(false));
				}}
			>
				<div className="flexRow" style={{ marginLeft: "-82vw", marginTop: "-15vh" }}>
					<Link href="/" ><Image className="logo" src={mxrLogo} alt="logo" title="logo" width={125} /></Link>
					<ColorThemeButton></ColorThemeButton>
				</div>
				<h1 style={{ fontSize: "40px" }}>Welcome back!</h1>
				<h1>Sign in to MusicMixxer</h1>
				<p className="muted-copy">
					Use your Mixxer account to access your sorted playlists, personalized dashboard, manage your connected services, and more.
				</p>
				<label className="field">
					<span>Email</span>
					<input
						required
						type="email"
						value={form.email}
						onChange={(event) =>
							setForm((current) => ({ ...current, email: event.target.value }))
						}
						placeholder="you@example.com"
					/>
				</label>
				<label className="field">
					<span>Password</span>
					<input
						required
						type="password"
						value={form.password}
						onChange={(event) =>
							setForm((current) => ({ ...current, password: event.target.value }))
						}
						placeholder="• • • • • • • •"
					/>
				</label>
				<label className="checkbox-row" style={{display: "flex", justifyContent: "center"}}>
					<input
						type="checkbox"
						checked={form.remember_me}
						onChange={(event) =>
							setForm((current) => ({
								...current,
								remember_me: event.target.checked,
							}))
						}
					/>
					<span>Keep me signed in on this browser</span>
				</label>
				{error ? <div className="notice error" style={{color: "black"}}>{error}</div> : null}
				<button className="primary-button" style={{color: "black"}} disabled={isSubmitting} type="submit">
					{isSubmitting ? "Signing in..." : "Sign in"}
				</button>
				<div className="flexColumn">
					<Link href="/account/signUp">Don't have an account?</Link>

				</div>
			</form>
		</main>
	);
}
