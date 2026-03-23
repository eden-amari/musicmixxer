import React from 'react';
import './Navbar.css';

type NavbarProps = {
  className?: string;
};


const Navbar = ({ className }: NavbarProps) => {
  return (
    <nav className={className}>
      <ul className="nav-links">
        <li className="li"><a href="/popNow">Popular Now</a></li>
        
        <p className='li'>|</p>
        
        <li className="li"><a href="/account">Account</a></li>
      </ul>
      
    </nav>
  );
};

export default Navbar;