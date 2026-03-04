import Image from "next/image";
import styles from "./page.module.css";
import Navbar from "./components/Navbar.js";

const welcomeH1 = "Hello! Welcome to Mixxer."
const welcomeH2="This is the index.js page."
export default function Home() {
	return (
	
	<><Navbar />
	<div className={styles.page}>
			<h1>Hello! Welcome to Mixxer.<br/>This is the index.js page.</h1>
		</div></>
	);


}

