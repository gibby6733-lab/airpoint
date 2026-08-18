import Link from "next/link";

export const metadata = {
  title: "Dew Point vs. Humidity | AirPoint",
  description:
    "Understand the difference between dew point and relative humidity and when each measurement is useful.",
};

export default function DewPointVsHumidity() {
  return (
    <main className="site">
      <section className="hero">
        <div className="container">
          <div className="badge">AIRPOINT GUIDE</div>

          <h1>Dew Point vs. Humidity</h1>

          <p className="heroText">
            They both describe moisture in the air, but they measure it in
            different ways.
          </p>

          <Link href="/" className="backLink">
            ← Calculate Dew Point
          </Link>
        </div>
      </section>

      <section className="content">
        <div className="container narrow">
          <h2>What is relative humidity?</h2>

          <p>
            Relative humidity describes how close the air is to being saturated
            with water vapor at its current temperature. It is normally
            expressed as a percentage.
          </p>

          <p>
            For example, 60% relative humidity means the air is holding about
            60% of the moisture it could hold at that particular temperature
            before becoming saturated.
          </p>

          <h2>What is dew point?</h2>

          <p>
            Dew point is the temperature at which the air would become
            saturated with water vapor. It is expressed as a temperature,
            usually in degrees Fahrenheit or Celsius.
          </p>

          <h2>The biggest difference</h2>

          <p>
            Relative humidity changes significantly when temperature changes,
            even if the amount of moisture in the air stays the same. Dew point
            is more directly related to the actual amount of moisture present.
          </p>

          <div className="infoCard">
            <strong>Simple way to remember it</strong>
            <p>
              Humidity tells you how full the air is relative to its current
              temperature. Dew point tells you how much the air would need to
              cool before becoming saturated.
            </p>
          </div>

          <h2>Which one should you use?</h2>

          <p>
            Relative humidity is useful when discussing indoor comfort,
            weather conditions, and moisture levels relative to temperature.
          </p>

          <p>
            Dew point is particularly useful when you want to understand how
            much moisture is actually in the air or whether condensation may
            form as surfaces cool.
          </p>

          <h2>Example</h2>

          <p>
            Imagine two days with the same 60% relative humidity. If one day is
            much warmer, the air can contain substantially more water vapor than
            on the cooler day.
          </p>

          <p>
            Their dew points would help reveal the difference in actual
            moisture content more clearly.
          </p>

          <h2>Calculate dew point</h2>

          <p>
            Enter your air temperature and relative humidity to calculate the
            dew point instantly.
          </p>

          <Link href="/" className="primaryLink">
            Open Dew Point Calculator →
          </Link>

          <h2>Related guides</h2>

          <ul className="linkList">
            <li>
              <Link href="/what-is-dew-point">What Is Dew Point?</Link>
            </li>
            <li>
              <Link href="/dew-point-chart">Dew Point Chart</Link>
            </li>
          </ul>
        </div>
      </section>
    </main>
  );
}