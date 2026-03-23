
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
    <Navbar/>
      <div className="flex flex-col flex-1 font-sans" style={{ backgroundColor: "white" }}>
        <div className="flex flex-row">
          
          <LeftPanel className="importLeftPanel">
            <br></br><br></br><br></br>
            <h1 className="h1">
              Import...
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

          
        </div>
        
        
      </div>
    </BrowserRouter>
  );
}
