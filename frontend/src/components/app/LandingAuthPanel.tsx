"use client";

import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "@/components/providers/AuthProvider";
import googleLogo from "@/assets/images/googleLogo.png";
import spotifyLogo from "@/assets/images/spotifyLogo.png";
import "/src/components/Buttons/Buttons.css"

type LandingAuthPanelProps = {
	googleClientId: string;
	isOpen?: boolean;
};

export function LandingAuthPanel({
	googleClientId,
	isOpen = true,
}: LandingAuthPanelProps) {
	const router = useRouter();
	const { signInWithGoogle } = useAuth();
	const [error, setError] = useState<string | null>(null);
	const [busy, setBusy] = useState<"google" | null>(null);
	const [googleButtonWidth, setGoogleButtonWidth] = useState(280);
	const googleConfiguredRef = useRef(false);
	const googleActionRef = useRef<HTMLDivElement | null>(null);
	const googleButtonRef = useRef<HTMLDivElement | null>(null);

	const initializeGoogle = useCallback(() => {
		const googleApi = (window as Window & {
			google?: {
				accounts?: {
					id?: {
						initialize: (config: {
							client_id: string;
							callback: (response: { credential?: string }) => void;
						}) => void;
						renderButton: (
							parent: HTMLElement,
							options: Record<string, string | number>,
						) => void;
					};
				};
			};
		}).google;

		if (!isOpen) {
			return false;
		}

		if (!googleClientId || !googleApi?.accounts?.id || !googleButtonRef.current || !googleButtonWidth) {
			return false;
		}

		if (!googleConfiguredRef.current) {
			googleApi.accounts.id.initialize({
				client_id: googleClientId,
				callback: ({ credential }) => {
					if (!credential) {
						setBusy(null);
						setError("Google sign-in did not return a credential.");
						return;
					}

					setError(null);
					setBusy("google");
					void signInWithGoogle(credential)
						.then(() => router.push("/account/dashboard"))
						.catch((nextError) => {
							setError(
								nextError instanceof Error
									? nextError.message
									: "Google sign-in failed.",
							);
						})
						.finally(() => setBusy(null));
				},
			});
			googleConfiguredRef.current = true;
		}

		googleButtonRef.current.innerHTML = "";
		googleApi.accounts.id.renderButton(googleButtonRef.current, {
			theme: "outline",
			size: "large",
			text: "continue_with",
			shape: "pill",
			logo_alignment: "left",
			width: googleButtonWidth,
		});

		return true;
	}, [googleButtonWidth, googleClientId, isOpen, router, signInWithGoogle]);

	useEffect(() => {
		if (!isOpen) {
			return;
		}

		const node = googleActionRef.current;
		if (!node) {
			return;
		}

		const updateWidth = () => {
			const nextWidth = Math.max(
				220,
				Math.min(Math.floor(node.getBoundingClientRect().width), 360),
			);
			setGoogleButtonWidth((current) => (current === nextWidth ? current : nextWidth));
		};

		updateWidth();

		if (typeof ResizeObserver === "undefined") {
			return;
		}

		const observer = new ResizeObserver(() => updateWidth());
		observer.observe(node);
		return () => observer.disconnect();
	}, [isOpen]);

	useEffect(() => {
		if (!isOpen) {
			return;
		}

		let timeout = 0;
		let attempts = 0;

		const tryInitialize = () => {
			if (initializeGoogle()) {
				return;
			}

			if (attempts >= 20) {
				return;
			}

			attempts += 1;
			timeout = window.setTimeout(tryInitialize, 250);
		};

		tryInitialize();

		return () => window.clearTimeout(timeout);
	}, [initializeGoogle, isOpen]);

	return (
		<section
			aria-hidden={!isOpen}
			className={isOpen ? "landing-auth-card landing-auth-card-compact open" : "landing-auth-card landing-auth-card-compact"}
			id="landing-auth-panel">

			<div className="google-action-area" ref={googleActionRef}>
				<div className="google-render-slot" ref={googleButtonRef} />
			</div>

			<div className="landing-auth-stack">
				{/* <div className="landing-auth-row google-auth-row">
					<div className="social-tile-meta">
						<div className="social-icon google-icon" aria-hidden="true">
							<Image alt="" className="social-logo" height={20} src={googleLogo} width={20} />
						</div>
						<div className="social-copy">
							<span>Continue with Google</span>
						</div>
					</div>

				</div> */}

				<button
					className="landing-auth-row landing-auth-row-button social-tile-button spotify-auth-button"
					type="button"
					onClick={() => {
						window.location.assign("/api/backend/auth/spotify/login");
					}}>

					<div className="social-tile-meta">
						<div className="social-icon spotify-icon" aria-hidden="true">
							<Image
								alt=""
								className="social-logo"
								height={20}
								src={spotifyLogo}
								width={20}
							/>
						</div>
						<div className="social-copy">
							<span>Continue with Spotify</span>
						</div>
					</div>
					{/* <div className="landing-inline-cta">Open Spotify</div> */}
				</button>

				<Link className="landing-auth-row landing-auth-row-link" href="/account/signIn">
					<div className="landing-auth-row-copy">
						<span>Sign in with email</span>
						<small>Use your existing Mixxer account details</small>
					</div>
					{/* <div className="landing-inline-cta">Open form</div> */}
				</Link>

				<Link className="landing-auth-row landing-auth-row-link" href="/account/signUp">
					<div className="landing-auth-row-copy">
						<span>Create account</span>
						<small>Start a fresh library!</small>
					</div>
					{/* <div className="landing-inline-cta secondary">Sign up</div> */}
				</Link>
			</div>

			{error ? <div className="notice error compact">{error}</div> : null}
		</section>
	);
}
