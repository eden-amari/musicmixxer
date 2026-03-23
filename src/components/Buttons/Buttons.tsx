import ColorSliver from "./ColorSliver";
function HomeImportButton() {
  return (
    <div>
      
      <ColorSliver/>
      <a href="/importPlaylist">
        <button className="homeImportButton agrandir">Import Playlist</button>
      </a>

    </div>
    
  );
}

export default HomeImportButton;

