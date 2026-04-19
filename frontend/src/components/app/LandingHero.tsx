"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import React from 'react'
import Image from "next/image";

import useEmblaCarousel from 'embla-carousel-react'

import { LandingAuthPanel } from "@/components/app/LandingAuthPanel";
import { useAuth } from "@/components/providers/AuthProvider";

//eden imports
import ReactPlayer from 'react-player'
import "/src/components/Buttons/Buttons.css"

import ReactDOM from 'react-dom/client'
import mxrLogo from "/src/assets/images/mxr.png";
import arrowPic from "/src/assets/images/refresh.png";
import arrowPicWhite from "/src/assets/images/refresh_white.png";
import { SongCard } from "@/components/SongCard/SongCard";

import "@/components/MainBlocks/Decor.css"
import "@/components/Buttons/Buttons.css";
import "@/components/MainBlocks/Panels.css";
import "@/components/Navbar/Navbar.css"
import "@/components/SongCard/SongCard.css"


import donnaAlbum from "/src/assets/images/donnaAlbumCover.jpeg";
import madonnaAlbum from "/src/assets/images/madonnaAlbumCover.jpg";
import newJeansAlbum from "/src/assets/images/newJeansAlbumCover.jpeg";
import mcrAlbum from "/src/assets/images/threecheerscover.png";
import { ColorThemeButton } from "../Buttons/Buttons";
// images

type LandingHeroProps = {
	googleClientId: string;
};

const landingHighlights = [
	{
		title: "Spotify + files",
		description: "Bring in the playlists you already use.",
	},
	{
		title: "Flow-first sorting",
		description: "Tune pacing around the energy you want.",
	},
	{
		title: "Ready to export",
		description: "Keep your final version easy to share.",
	},
] as const;

const landingMetrics = [
	{ value: "Spotify", label: "Native import" },
	{ value: "CSV + JSON", label: "File support" },
	{ value: "Flow-first", label: "Sorting approach" },
] as const;

const workflowCards = [
	{
		kicker: "Import",
		title: "Pull your playlists from Spotify or local files",
		description: "No need to start from scratch!",
	},
	{
		kicker: "Organize",
		title: "Reorder by BPM, mood, or momentum",
		description: "Make your music waaaaay smoother.",
	},
	{
		kicker: "Export",
		title: "Get the polished version back",
		description: "Your playlist is now ready for listening, sharing, or exporting.",
	},
] as const;

// const albumCovers = {
// 	donna: donnaAlbum,
// 	madonna: madonnaAlbum,
// 	newJeans: newJeansAlbum,
// 	mcr: mcrAlbum,
// };


var cardCarousel = [
	["Donna Summer", "Hot Stuff (VH1 1999)", "/src/assets/images/donnaAlbumCover.jpeg", "/videos/donna1999.mp4"],
	["Madonna", "Vogue (MTV 1990)", "/src/assets/images/madonnaAlbumCover.jpg", "/videos/madonnaVogueLive.mp4"],
	["New Jeans", "Cookie", "/src/assets/images/newJeansAlbumCover.jpeg", "/videos/newJeansMV.mp4"],
	["My Chemical Romance", "Helena", "/src/assets/images/threecheerscover.png", "/videos/mcrHelenaMV.mp4"],
]
// <ReactPlayer className="" src="/videos/newJeansMV.mp4" height="100vw" width="100vh" controls={false} autoPlay={true} loop={true} muted={true} />

export function LandingHero({ googleClientId }: LandingHeroProps) {

	const router = useRouter();
	const { isReady, session } = useAuth();
	const [authOpen, setAuthOpen] = useState(false);
	const authShellRef = useRef<HTMLDivElement | null>(null);

	const [currentTheme, setCurrentTheme] = useState("donna");
	const [songTitle, setSongTitle] = useState("Hot Stuff (VH1 1999)");
	const [songArtist, setSongArtist] = useState("Donna Summer");
	const themes = ["donna", "madonna", "newJeans", "mcr"];

	const getButtonStyle = (theme: string) => {
		switch (theme) {
			case "donna": return { backgroundColor: "#184b8c" };
			case "madonna": return { backgroundColor: "#d388a3" };
			case "newJeans": return { backgroundColor: "#bb9ae0" };
			case "mcr": return { backgroundColor: "#194355" };
			default: return {};
		}
	};

	let blobBG = getButtonStyle(currentTheme).backgroundColor
	console.log(blobBG);

	const getKickerStyle = (theme: string) => {
		switch (theme) {
			case "donna": return { backgroundColor: "#ffc9e8" };
			case "madonna": return { backgroundColor: "#f6b9cf" };
			case "newJeans": return { backgroundColor: "#ead7ff" };
			case "mcr": return { backgroundColor: "#7e1f1f", color: "white" };
			default: return {};
		}
	};

	const routeThroughAuth = (destination: "/organizePlaylist/import" | "/account/dashboard") => {
		if (!isReady || !session) {
			setAuthOpen(true);
			return;
		}

		router.push(destination);
	};

	useEffect(() => {
		document.body.className = currentTheme;
	}, [currentTheme]);


	// function PageToggleDonna() {

	return (

		<section className="hero-card landing-hero landing-hero-minimal" data-theme={currentTheme} id="heroMain">


			<div className="landing-topbar">

				<div className="landing-brand-lockup">
					<Link href="/">
						<Image className="logo" src={mxrLogo} alt="logo" title="logo" width={125} style={{ marginLeft: "-1.5vw" }} />
						<span className="landing-brand-text">
							{/* <h1>Welcome to Mixxer!</h1> */}
							<small >Playlist organization that feels intentional</small>
						</span>
					</Link>

					<div className="flexRow" style={{ marginLeft: "50vw" }}>

						{/* Theme toggle button */}
						<button
							className="colorThemeButton" style={{ display: "flex", alignItems: "center", justifyContent: "center", ...getButtonStyle(currentTheme) }}


							onClick={() => {
								const currentIndex = themes.indexOf(currentTheme);
								const nextIndex = (currentIndex + 1) % themes.length;
								setCurrentTheme(themes[nextIndex]);
								setSongTitle(cardCarousel[nextIndex][1]);
								setSongArtist(cardCarousel[nextIndex][0]);
							}}
						>
							<Image alt="" className="social-logo" height={20} src={arrowPicWhite} width={20} />
						</button>


						<div className="landing-auth-shell" ref={authShellRef} >
							<button
								aria-controls="landing-auth-panel"
								aria-expanded={authOpen ? "true" : "false"}
								className={authOpen ? "landing-signin-trigger active" : "landing-signin-trigger"}
								type="button"
								onClick={() => setAuthOpen((current) => !current)}
							>
								{authOpen ? "Account" : "Account"}
							</button>
							<div className={authOpen ? "landing-auth-popover open" : "landing-auth-popover"}>
								<LandingAuthPanel googleClientId={googleClientId} isOpen={authOpen} />
							</div>
						</div>

					</div>


				</div>



			</div>

			<div className="landing-stage">
				<div className="landing-stage-grid">
					<div className="landing-intro landing-intro-minimal">

						<h1>Organize. Share. Enjoy.</h1>
						<p className="hero-copy">
							Reshape your playlists to create seamless transitions and a more enjoyable listening experience! Mixxer helps you focus on the flow of your music instead of spending hours on manual organization.

						</p>
						<div className="landing-inline-actions">
							<button
								className="primary-button"

								type="button"
								onClick={() => routeThroughAuth("/organizePlaylist/import")}
							>
								Start organizing
							</button>

						</div>
						<div className="landing-metric-row" aria-label="Key product metrics" style={{ marginBottom: "2vh" }}>
							{landingMetrics.map((metric) => (
								<div className="landing-metric-card" key={metric.label} >
									<strong>{metric.value}</strong>
									<span>{metric.label}</span>
								</div>
							))}
						</div>

						<div className="landing-showcase-grid" >
							{workflowCards.map((card) => (
								<article className="landing-showcase-card" key={card.title}>
									<div className="landing-showcase-kicker" style={getKickerStyle(currentTheme)}>{card.kicker}</div>
									<strong>{card.title}</strong>
									<p>{card.description}</p>
								</article>
							))}

						</div>


					</div>
					{/* <div className="landing-showcase-chip">

										</div> */}



					<div className="landing-showcase">
						<div className="landing-showcase-panel" style={{ "zIndex": "-2" }}>

							<video key={currentTheme} className={`${currentTheme}Video`} style={{ width: "100vw", height: "80vh", objectFit: "cover", borderRadius: "24px", position: "relative", zIndex: -1 }} autoPlay loop muted>
								<source src={cardCarousel[themes.indexOf(currentTheme)][3]} type="video/mp4"></source>
							</video>

							<div className="songBlob" style={{ backgroundColor: `${blobBG}`, color: "white", marginTop: "-8vh" }}>{songTitle} | {songArtist}</div>



						</div>

					</div>
				</div>
			</div>


		</section>
	);
}
