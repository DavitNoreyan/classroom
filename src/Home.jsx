import React from "react";
import web from "../src/image/getStarted.png";
import Common from "./Common";

function Home() {
  return (
    <>
      <Common
        name="Start learning programming with"
        imgsrc={web}
        visit="/service"
        btname="Get Started"
        about="We are ready to teach you the basics of programming"
      />
    </>
  );
}

export default Home;
