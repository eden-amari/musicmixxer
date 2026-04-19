"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useAuth } from "@/components/providers/AuthProvider";
import "/src/components/Buttons/Buttons.css"
import { ColorThemeButton } from "@/components/Buttons/Buttons";
import mxrLogo from "/src/assets/images/mxr.png";
import Image from "next/image";


export default function SignUpPage() {
	const router = useRouter();
	const { signUp } = useAuth();
	const [form, setForm] = useState({
		username: "",
		email: "",
		password1: "",
		password2: "",
	});
	const [error, setError] = useState<string | null>(null);
	const [isSubmitting, setIsSubmitting] = useState(false);

	return (
		<main className="auth-shell">
			<form
				className="auth-card"
				onSubmit={(event) => {
					event.preventDefault();
					if (form.password1 !== form.password2) {
						setError("Passwords do not match.");
						return;
					}
					setIsSubmitting(true);
					setError(null);
					void signUp(form)
						.then(() => router.push("/account/dashboard"))
						.catch((nextError) => {
							setError(
								nextError instanceof Error ? nextError.message : "Unable to create account.",
							);
						})
						.finally(() => setIsSubmitting(false));
				}}
			>
				<div className="flexRow" style={{marginLeft: "-82vw", marginTop: "-5vh"}}>
					<Link href="/" ><Image className="logo" src={mxrLogo} alt="logo" title="logo" width={125}  /></Link>
					<ColorThemeButton></ColorThemeButton>
				</div>

				<h1 style={{fontSize: "40px"}}>New account</h1>
				<h1>Create your workspace</h1>
				<p className="muted-copy">
					Create an account with us to access your personalized dashboard, manage your connected services, and more.
				</p>
				<label className="field">
					<span>Username</span>
					<input
						required
						value={form.username}
						onChange={(event) =>
							setForm((current) => ({ ...current, username: event.target.value }))
						}
						placeholder="mixmaster"
					/>
				</label>
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
						value={form.password1}
						onChange={(event) =>
							setForm((current) => ({ ...current, password1: event.target.value }))
						}
						placeholder="• • • • • • • •"
					/>
				</label>
				<label className="field">
					<span>Confirm password</span>
					<input
						required
						type="password"
						value={form.password2}
						onChange={(event) =>
							setForm((current) => ({ ...current, password2: event.target.value }))
						}
						placeholder="• • • • • • • •"
					/>
				</label>

				<div className="flexColumn" style={{display: "flex", justifyContent: "center", alignItems: "center"}}>

				{error ? <div className="notice error">{error}</div> : null}
								<button style={{color:"black"}} disabled={isSubmitting} type="submit">
									{isSubmitting ? "Creating account..." : "Create account"}
								</button>
				<Link href="/account/signIn">Already have an account?</Link>
				</div>
			</form>
		</main>
	);
}
