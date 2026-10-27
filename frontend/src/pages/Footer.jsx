import { Link } from 'react-router-dom';
import logoImg from '../assets/IIA.png'

export default function Footer() {
    return (
        <footer>
            <div class="site-footer">
                <img src={logoImg} class="footer-logo" alt="" />
                <h2>Is it AI</h2>
            </div>
            <div class="footer-content">
                <div class="footer-column">
                    <div>
                        <h3>Contact Us</h3>
                        <hr />
                        <h4>E-mail</h4>
                        <a href="mailto:info@isitai.com.au">info@isitai.com.au</a>
                    </div>
                    <div>
                        <h4>Phone</h4>
                        <p>1800 000 000</p>
                    </div>
                </div>
                <div class="footer-column">
                    <h3>Pages</h3>
                    <hr />
                    <Link to="/" alt="Check Page" hover="Check">Check</Link>
                    <Link to="/about" alt="About Page" hover="About">About</Link>
                    <Link to="/faq" alt="Frequently Asked Questions" hover="FAQ">FAQ</Link>
                </div>
                <div>
                    <div></div>
                    <div></div>
                </div>
            </div>
        </footer>
    );
}