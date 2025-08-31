import Lottie from "lottie-react";
import weatherLottie from "@/lotties/weatherCloudy.json";

export default function WeatherCloudy() {
  const style = {
    height: 80,
  };

  return <Lottie animationData={weatherLottie} style={style} loop={true} />;
}
