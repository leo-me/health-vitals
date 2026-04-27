import { Navbar } from "./components/NavBar";
import { Hero } from "./components/Hero";
import { TrustBar } from "./components/TrustBard";
import { Features } from "./components/Features";
import { Footer } from "./components/Footer";

import '@/app/globals.css'



export default function HomePage() {
  return (
    <div className="min-h-screen home" >
      <Navbar />
      <main>
        <Hero />
        <TrustBar />
        <Features />
      </main>
      <Footer />
    </div>
  );
}
