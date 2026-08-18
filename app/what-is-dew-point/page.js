import Link from "next/link";

export const metadata = {
  title: "What Is Dew Point? | AirPoint",
  description:
    "Learn what dew point means, how it relates to humidity, and when condensation can occur.",
};

export default function WhatIsDewPoint() {
  return (
    <main className="site">
      <section className="hero">
        <div className="container">
          <div className="badge">AIRPOINT GUIDE</div>

          <h1>What Is Dew Point?</h1>

          <p className="heroText">
            A simple explanation of dew point, humidity, condensation, and why
            the temperature matters.
          </p>

          <Link href="/" className="backLink">
            ← Calculate Dew Point
          </Link>
        </div>
      </section>

      <section className="content">
        <div className="container narrow">
          <h2>Dew point explained</h2>

          <p>
            Dew point is the temperature at which air becomes saturated with
            water vapor. If the air is cooled to its dew point, water vapor can
            begin changing into liquid water.
          </p>

          <p>
            In simple terms, dew point tells you how much moisture is actually
            present in the air. A higher dew point generally means more
            moisture.
          </p>

          <h2>Dew point vs. temperature</h2>

          <p>
            Air temperature and dew point are related, but they are not the
            same thing. Air temperature tells you how warm or cold the air is.
            Dew point tells you the temperature at which that air would become
            saturated.
          </p>

          <p>
            When the air temperature gets close to the dew point, the air is
            relatively humid. When the two temperatures are far apart, the air
            is generally drier.
          </p>

          <h2>When does condensation happen?</h2>

          <p>
            Condensation can form when a surface becomes colder than the
            surrounding air's dew point. This is why water can appear on cold
            windows, pipes, vehicles, and other surfaces.
          </p>

          <p>
            For example, if the air has a dew point of 18°C and a window surface
            cools below 18°C, condensation can begin forming on that window.
          </p>

          <h2>Why dew point matters</h2>

          <p>
            Dew point is useful in weather forecasting, HVAC, building
            management, agriculture, outdoor activities, and moisture
            monitoring.
          </p>

          <p>
            Unlike relative humidity, dew point is less dependent on the
            current air temperature, which makes it useful for understanding
            how much moisture is actually in the air.
          </p>

          <h2>How is dew point calculated?</h2>

          <p>
            AirPoint estimates dew point using air temperature and relative
            humidity. The calculation uses a standard approximation based on
            the relationship between temperature and water-vapor saturation.
          </p>

          <div className="infoCard">
            <strong>Want to calculate it?</strong>
            <p>
              Enter your temperature and relative humidity in the AirPoint
              calculator to get an instant dew point result.
            </p>

            <Link href="/" className="primaryLink">
              Open Dew Point Calculator →
            </Link>
          </div>

          <h2>Related AirPoint tools</h2>

          <ul className="linkList">
            <li>
              <Link href="/dew-point-chart">Dew Point Chart</Link>
            </li>
            <li>
              <Link href="/dew-point-vs-humidity">
                Dew Point vs. Humidity
              </Link>
            </li>
          </ul>
        </div>
      </section>
    </main>
  );
}