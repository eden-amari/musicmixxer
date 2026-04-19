"use client";
import { useEffect, useRef, useState } from "react";
import arrowPicWhite from "/src/assets/images/refresh_white.png";
import Image from "next/image";
import ColorSliver from "./ColorSliver";
function HomeImportButton() {
	return (
		<div>
			<ColorSliver />
			<a href="/organizePlaylist/import">
				<button className="homeImportButton agrandir">
					Import Playlist
				</button>
			</a>
		</div>
	);
}
export default HomeImportButton;
// ---------------------------------------

type SubmitButtonProps = {
	className?: string;
	onClick?: () => void;
	disabled?: boolean;
	style?: React.CSSProperties;
	link?: string;
};
export function SubmitButton({
	className,
	onClick,
	disabled,
	style,
	link,
}: SubmitButtonProps) {
	const classes = ["SubmitButton", className, style, link]
		.filter(Boolean)
		.join(" ");
	return (
		<div>
			{/* <ColorSliver/> */}
			<a href={link}>
				<button
					type="submit"
					className={classes}
					onClick={onClick}
					disabled={disabled}
					style={style}
				>
					Submit
				</button>
			</a>
		</div>
	);
}

// ---------------------------------------
export function Checkbox() {
	const [checked, setchecked] = useState(false);
	return (
		<div
			style={{
				justifyContent: "space-between",
				display: "flex",
				width: "22vw",
				marginBottom: ".5vh",
				marginTop: "1vh",
			}}
		>
			<label className="p" style={{ color: "#9396a7" }}>
				<input
					style={{ marginLeft: "10px" }}
					type="checkbox"
					checked={checked}
					onChange={(e) => {
						setchecked(e.target.checked);
					}}
				/>{" "}
				Remember Me
			</label>

			<a
				href="/account/forgotPassword"
				className="forgotPassword p"
				style={{ color: "#9396a7" }}
			>
				Forgot Password?
			</a>
		</div>
	);
}
// ---------------------------------
const getButtonStyle = (theme: string) => {
	switch (theme) {
		case "donna": return { backgroundColor: "#184b8c" };
		case "madonna": return { backgroundColor: "#d388a3" };
		case "newJeans": return { backgroundColor: "#bb9ae0" };
		case "mcr": return { backgroundColor: "#194355" };
		default: return {};
	}
};



var cardCarousel = [
	["Donna Summer", "Hot Stuff (VH1 1999)", "/src/assets/images/donnaAlbumCover.jpeg", "/videos/donna1999.mp4"],
	["Madonna", "Vogue (MTV 1990)", "/src/assets/images/madonnaAlbumCover.jpg", "/videos/madonnaVogueLive.mp4"],
	["New Jeans", "Cookie", "/src/assets/images/newJeansAlbumCover.jpeg", "/videos/newJeansMV.mp4"],
	["My Chemical Romance", "Helena", "/src/assets/images/threecheerscover.png", "/videos/mcrHelenaMV.mp4"],
]
export function ColorThemeButton() {

	const [currentTheme, setCurrentTheme] = useState("donna");
	const [songTitle, setSongTitle] = useState("Hot Stuff (VH1 1999)");
	const [songArtist, setSongArtist] = useState("Donna Summer");
	const themes = ["donna", "madonna", "newJeans", "mcr"];
	useEffect(() => {
		document.body.className = currentTheme;
	}, [currentTheme]);

	let blobBG = getButtonStyle(currentTheme).backgroundColor
	return (

		<button

			className="colorThemeButton" style={{ display: "flex", alignItems: "center", justifyContent: "center", ...getButtonStyle(currentTheme) }}


			onClick={() => {
				const currentIndex = themes.indexOf(currentTheme);
				const nextIndex = (currentIndex + 1) % themes.length;
				setCurrentTheme(themes[nextIndex]);
				setSongTitle(cardCarousel[nextIndex][1]);
				setSongArtist(cardCarousel[nextIndex][0]);

				// let changeText = document.documentElement.getElementsByClassName("change2white")[0] as HTMLElement;
				// if (currentTheme == "newJeans") {
				// 	changeText.style.color = "#ffffff"; }
				// else { changeText.style.color = "#000000"; }
			}}
		>
			<Image alt="" className="social-logo" height={20} src={arrowPicWhite} width={20} />
		</button>

	);

}
// ---------------------------------------
// type SubmitButtonProps = {
//   className?: string;
//   onClick?: () => void;
//   disabled?: boolean;
//   style?: React.CSSProperties;
// };
// export function SubmitButton({ className, onClick, disabled, style}: SubmitButtonProps) {
//   const classes = ["SubmitButton", className, style].filter(Boolean).join(" ");
//   return (
//     <div>

//       {/* <ColorSliver/> */}
//       <a href="/importPlaylist">
//         <button className={classes} onClick={onClick} disabled={disabled} style={style}>
//           <p className="p">Submit</p>
//         </button>
//       </a>
//     </div>
//   );
// }

// ---------------------------------------
// type LoginSignupProps = {
//     className?: string;
//   };

// ------------------------
// export function DarkModeButton() {
//   return (
//     <div>
//       <button className="darkModeButton agrandir" onClick={() => { isDarkMode = true; change2DarkMode(); }}>Dark Mode</button>

//     </div>

//   );
// }

// export function change2DarkMode() {
//   document.documentElement.style.setProperty('--headings', darkModeColors.headings);
//   document.documentElement.style.setProperty('--bubbleBackground', darkModeColors.bubbleBackground);
//   document.documentElement.style.setProperty('--bubbleText', darkModeColors.bubbleText);
//   document.documentElement.style.setProperty('--grayText', darkModeColors.grayText);
//   document.documentElement.style.setProperty('--boxBackground', darkModeColors.boxBackground);
//   document.documentElement.style.setProperty('--fullBackground', darkModeColors.fullBackground);
//   document.documentElement.style.setProperty('--accent1', darkModeColors.accent1);
//   document.documentElement.style.setProperty('--accent2', darkModeColors.accent2);

// }

// export function LightModeButton() {
//   return (
//     <button className="lightModeButton agrandir" onClick={() => change2LightMode()}>Light Mode</button>

//   );
// }

// export function change2LightMode() {
//   document.documentElement.style.setProperty('--headings', lightModeColors.headings);
//   document.documentElement.style.setProperty('--bubbleBackground', lightModeColors.bubbleBackground);
//   document.documentElement.style.setProperty('--bubbleText', lightModeColors.bubbleText);
//   document.documentElement.style.setProperty('--grayText', lightModeColors.grayText);
//   document.documentElement.style.setProperty('--boxBackground', lightModeColors.boxBackground);
//   document.documentElement.style.setProperty('--fullBackground', lightModeColors.fullBackground);
//   document.documentElement.style.setProperty('--accent1', lightModeColors.accent1);
//   document.documentElement.style.setProperty('--accent2', lightModeColors.accent2);
// }

// const lightModeColors = {
//   headings: "#000000",
//   bubbleBackground: "#2e2f33",
//   bubbleText: "#ffffff",
//   grayText: "#9396a7",
//   boxBackground: "#ffffff",
//   fullBackground: "#2e2f33",
//   accent1: "#99acff",
//   accent2: "#6b7bd0",

// };

// const darkModeColors = {
//   headings: "#ffffff",
//   bubbleBackground: "#ffffff",
//   bubbleText: "#000000",
//   grayText: "#9396a7",
//   boxBackground: "#2e2f33",
//   fullBackground: "#000000",
//   accent1: "#99acff",
//   accent2: "#6b7bd0",

// };

// export function colorChange() {
//   function handleClick() {
//     alert('You clicked me! Changing color now.');
//   }

//   if (isDarkMode) {
//     change2LightMode();
//   } else {
//     change2DarkMode();
//   }
//   isDarkMode = !isDarkMode;
// }

// export function ThemeToggle({ themeSwitch = f => f }) {
//   return (
//     <button
//       className="themeToggle"
//       type="button"
//       onClick={themeSwitch}
//       aria-label="change theme color"
//     />
//   )
// }
