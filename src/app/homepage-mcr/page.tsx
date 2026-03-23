import Image from "next/image";
import HomeImportButton from "@/components/Buttons/Buttons";
import {LeftPanel} from "@/components/MainBlocks/Panels";
import {RightPanel} from "@/components/MainBlocks/Panels";
import "@/components/Navbar/Navbar"
import "@/components/Buttons/ColorSliver"
import "@/components/SongCard/SongCard"

import "@/components/MainBlocks/Decor.css"
import "@/components/Buttons/Buttons.css";
import "@/components/MainBlocks/Panels.css";
import "@/components/Navbar/Navbar.css"
import "@/components/SongCard/SongCard.css"

import mcrAlbum from "@/assets/images/threecheerscover.png";
import localFont from "next/font/local";
import "@/app/globals.css";
import Navbar from "@/components/Navbar/Navbar";
import { ColorSliver } from "@/components/Buttons/ColorSliver";
import { SongCard } from "@/components/SongCard/SongCard";

import React from 'react'
import ReactPlayer from 'react-player'




function Home() {
  return (
    <div className="flex flex-col flex-1 bg-zinc-50 font-sans dark:bg-white">
      <div className="flex flex-row">
        
        <LeftPanel className="leftmcrBig ">
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
            <ColorSliver className="mcrColorSliver" />
            <HomeImportButton/>
          </div>
          
        </LeftPanel>
        
        <LeftPanel className="leftmcrSmall" />

        <RightPanel className="rightmcr"> 
         
          <Navbar className="mcrNavbar" />
{/*           
          <hr className="mcrNavHR"></hr> */}
          <ReactPlayer className="mcrVideo" src="/videos/mcrHelenaMV.mp4" height="100vh" width="100vw"  controls={false} autoPlay={true} loop={true} muted={true} />
          <SongCard className="mcrCard align-items:center z-index:1">
            <Image className="photocard " src={mcrAlbum} alt="Three Cheers For Sweet Revenge, MCR Album Cover" title="Three Cheers For Sweet Revenge - MCR Album Cover" />
            <div className="songTitle" style={{ backgroundColor: "black", color: "white" }}>HELENA</div>
            <div className="songArtist" style={{ backgroundColor: "white", color: "black" }}>My Chemical Romance</div>
            
            
          </SongCard>
          <div className="carouselButtons">
              <a href="/homepage-newJeans"><button className="circularButtonLeft mcrCircle">←</button></a>
              <a href="/"><button className="circularButtonRight mcrCircle">→</button></a>
            </div>
        </RightPanel>
      </div>
      
      
    </div>
  );
}
export default Home;

// mcr color sliver