"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/components/providers/AuthProvider";
import { useState } from "react";
import "/src/components/Buttons/Buttons.css"
import { ColorThemeButton } from "@/components/Buttons/Buttons";
import mxrLogo from "/src/assets/images/mxr.png";
import Image from "next/image";


const navItems = [
	{ href: "/account/dashboard", label: "Dashboard" },
	{ href: "/organizePlaylist/import", label: "Import" },
	{ href: "/organizePlaylist/export", label: "Export" },
];


export function AppHeader() {
	const pathname = usePathname();
	const router = useRouter();
	const { session, signOut } = useAuth();

	return (
		<header className="app-header change2white">
			<Link className="brand-lockup change2white" href="/">

			</Link>
			<nav className="flexRow" aria-label="Primary">
				<div className="flexRow" style={{ marginLeft: "-25vw",  marginRight: "20vw"}}>
					<Link href="/" ><Image className="logo" src={mxrLogo} alt="logo" title="logo" width={125} /></Link>
					<ColorThemeButton></ColorThemeButton>
				</div>
				{navItems.map((item) => (
					<div className="change2white">
					<Link
						key={item.href}
						className={pathname === item.href ? "nav-link active " : "nav-link "}
						href={item.href}
					>
						{item.label}
					</Link></div>
				))}
			</nav>
			<div className="change2white header-actions">
				{session ? (
					<>
						<div className="change2white user-chip ">
							<span >{session.user.username}</span>
							<small >{session.user.email}</small>
						</div>
						<button
							className="secondary-button ghost-button"
							type="button"
							onClick={async () => {
								await signOut();
								router.push("/account/signIn");
							}}
						>
							Sign out
						</button>
					</>
				) : (
					<>
						<Link className="ghost-button" href="/account/signIn">
							Sign in
						</Link>
						<Link className="primary-button" href="/account/signUp">
							Create account
						</Link>
					</>
				)}
			</div>
		</header>
	);
}
