import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/components/providers/AuthProvider";

export const metadata: Metadata = {
	title: "MusicMixxer",
	description: "Stateless playlist organization with a frontend-owned session.",
};

export default function RootLayout({
	children,
}: Readonly<{
	children: React.ReactNode;
}>) {
	return (
		<html lang="en">
			<body background-color="#ffc9e8">
				<AuthProvider>{children}</AuthProvider>
			</body>
		</html>
	);
}
