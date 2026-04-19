
import { AppHeader } from "@/components/app/AppHeader";
import { RequireAuth } from "@/components/app/RequireAuth";
import { WorkspaceClient } from "@/components/app/WorkspaceClient";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useAuth } from "@/components/providers/AuthProvider";
import "/src/components/Buttons/Buttons.css"
import { ColorThemeButton } from "@/components/Buttons/Buttons";
import mxrLogo from "/src/assets/images/mxr.png";
import Image from "next/image";
import ReactDOM from 'react-dom/client'


export default function DashboardPage() {

	return (
		<main className="flexColumnLeft change2white  page-shell">

			<AppHeader />
			<RequireAuth>
				<WorkspaceClient initialSection="dashboard" />
			</RequireAuth>
		</main>
	);
}
