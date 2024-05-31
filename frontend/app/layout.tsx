import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./styles/globals.css";

const inter = Inter({ subsets: ["latin"] });

interface LayoutProps {
  children: React.ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  return (
    <html>
      <body>
    <div>
      <header>
        <h1>FinAdvisory</h1>
      </header>
      <main>{children}</main>
      <footer>
        <p>© 2024 FinAdvisory</p>
      </footer>
    </div>
    </body>
    </html>
  );
};

export default Layout;
