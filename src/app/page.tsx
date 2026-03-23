
// Standard Imports ------------------------------------------------------
import Image from "next/image";

import { BrowserRouter } from "react-router-dom";

import React from 'react'
import ReactPlayer from 'react-player'

// Component Imports ------------------------------------------------------
import HomeImportButton from "@/components/Buttons/Buttons";
import {LeftPanel} from "@/components/MainBlocks/Panels";
import {RightPanel} from "@/components/MainBlocks/Panels";
import "@/components/Navbar/Navbar"
import "@/components/Buttons/ColorSliver"
import "@/components/SongCard/SongCard"


// CSS Imports ------------------------------------------------------
import "@/components/MainBlocks/Decor.css"
import "@/components/Buttons/Buttons.css";
import "@/components/MainBlocks/Panels.css";
import "@/components/Navbar/Navbar.css"
import "@/components/SongCard/SongCard.css"


// Asset Imports Imports ------------------------------------------------------
import donnaAlbum from "@/assets/images/donnaAlbumCover.jpeg";
import localFont from "next/font/local";
import "@/app/globals.css";
import Navbar from "@/components/Navbar/Navbar";
import { ColorSliver } from "@/components/Buttons/ColorSliver";
import { SongCard } from "@/components/SongCard/SongCard";



export default function Home() {
  return (
    <BrowserRouter>
      <div className="flex flex-col flex-1 font-sans" style={{ backgroundColor: "#0a2f5e" }}>
        <div className="flex flex-row">
          
          <LeftPanel className="leftDonnaBig ">
            <br></br><br></br><br></br>
            <h1 className="h1">
              Welcome to Mixxer!
            </h1>
            <h3 className="h3">Organize. Share. Enjoy.</h3>
            <hr className="hr"></hr>

            <p className="welcomeText">
              Enhance your listening experience by organizing your playlist--sort by BPM, mood, and genre to create seamless transitions.
            </p>

            <div className="buttonHolder"> 
              <ColorSliver className="donnaColorSliver" />
              <HomeImportButton/>
            </div>
            
          </LeftPanel>
          
          <LeftPanel className="leftDonnaSmall" />

          <RightPanel className="rightDonna"> 
          
            <Navbar className="donnaNavbar" />
            
            <hr className="donnaNavHR"></hr>
            <ReactPlayer className="donnaVideo" src="/videos/donna1999.mp4" height="100vh" width="100vw"  controls={false} autoPlay={true} loop={true} muted={true} />
            <SongCard className="donnaCard align-items:center z-index:1">
              <Image className="photocard " src={donnaAlbum} alt="Bad Girls, Donna Summer Album Cover" title="Bad Girls - Donna Summer Album Cover" />
              <div className="songTitle" style={{ backgroundColor: "#ffc9e8", color: "black" }}>HOT STUFF</div>
              <div className="songArtist" style={{ backgroundColor: "white", color: "black" }}>Donna Summer</div>
            </SongCard>
            <div className="carouselButtons">
              <a href="/homepage-mcr"><button className="circularButtonLeft donnaCircle">←</button></a>
              <a href="/homepage-madonna"><button className="circularButtonRight donnaCircle">→</button></a>
            </div>
            
          </RightPanel>
        </div>
        
        
      </div>
    </BrowserRouter>
  );
}
