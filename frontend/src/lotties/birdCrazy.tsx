import Lottie from "lottie-react";
import birdCrazyLottie from "@/lotties/birdCrazy.json";

export default function BirdCrazy() {
  const style = {
    height: 180,
  };

  return <Lottie animationData={birdCrazyLottie} style={style} loop={true} />;
}
