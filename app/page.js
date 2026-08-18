"use client";

import { useState } from "react";

function calculateDewPoint(tempC, humidity) {
  const a = 17.27;
  const b = 237.7;

  const gamma =
    (a * tempC) / (b + tempC) + Math.log(humidity / 100);

  return (b * gamma) / (a - gamma);
}

function cToF(c) {
  return (c * 9) / 5 + 32;
}

function fToC(f) {
  return ((f - 32) * 5) / 9;
}

function getRisk(dewPoint, temperature) {
  const difference = temperature - dewPoint;

  if (difference <= 2) {
    return {
      label: "High condensation risk",
      text: "The air temperature is very close to the dew point. Condensation can form on cooler surfaces.",
    };
  }

  if (difference <= 5) {
    return {
      label: "Moderate condensation risk",
      text: "Conditions are getting close to the dew point. Watch for condensation on cold surfaces.",
    };
  }

  return {
    label: "Low condensation risk",
    text: "There is a larger gap between the air temperature and dew point, so condensation is less likely.",
  };
}

export default function Home() {
  const [temperature, setTemperature] = useState("25");
  const [humidity, setHumidity] = useState("60");
  const [unit, setUnit] = useState("C");
  const [result, setResult] = useState(null);

  function calculate() {
    const temp = Number(temperature);
    const rh = Number(humidity);

    if (!Number.isFinite(temp) || !Number.isFinite(rh)) return;
    if (rh <= 0 || rh > 100) return;

    const tempC = unit === "C" ? temp : fToC(temp);
    const dewPointC = calculateDewPoint(tempC, rh);

    setResult({
      c: dewPointC,
      f: cToF(dewPointC),
      risk: getRisk(dewPointC, tempC),
    });
  }

  return (
    <main className="site">
      <section className="hero">
        <div className="container">
          <div className="badge">AIRPOINT</div>

          <h1>Dew Point Calculator</h1>

          <p className="heroText">
            Calculate dew point instantly from air temperature and relative
            humidity.
          </p>

          <div className="calculator">
            <div className="field">
              <label>Temperature</label>
              <div className="inputRow">
                <input
                  type="number"
                  value={temperature}
                  onChange={(e) => setTemperature(e.target.value)}
                />

                <select
                  value={unit}
                  onChange={(e) => setUnit(e.target.value)}
                >
                  <option value="C">°C</option>
                  <option value="F">°F</option>
                </select>
              </div>
            </div>

            <div className="field">
              <label>Relative Humidity</label>
              <div className="inputRow">
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={humidity}
                  onChange={(e) => setHumidity(e.target.value)}
                />
                <span className="unit">%</span>
              </div>
            </div>

            <button onClick={calculate}>Calculate Dew Point</button>

            {result && (
              <div className="result">
                <span className="resultLabel">DEW POINT</span>

                <div className="resultNumber">
                  {unit === "C"
                    ? `${result.c.toFixed(1)}°C`
                    : `${result.f.toFixed(1)}°F`}
                </div>

                <div className="secondary">
                  {unit === "C"
                    ? `${result.f.toFixed(1)}°F`
                    : `${result.c.toFixed(1)}°C`}
                </div>

                <div className="risk">
                  <strong>{result.risk.label}</strong>
                  <p>{result.risk.text}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      <section className="content">
        <div className="container narrow">
          <h2>What is dew point?</h2>

          <p>
            Dew point is the temperature at which air becomes saturated with
            water vapor. When a surface is cooled below the dew point,
            condensation can begin to form.
          </p>

          <p>
            Dew point is useful for understanding humidity, condensation,
            weather conditions, indoor comfort, HVAC performance, and moisture
            risk.
          </p>

          <h2>How to calculate dew point</h2>

          <p>
            AirPoint calculates dew point using air temperature and relative
            humidity. The calculation uses a standard approximation of the
            relationship between temperature, humidity, and water vapor.
          </p>

          <h2>Dew point and condensation</h2>

          <p>
            The closer the air temperature is to the dew point, the easier it
            is for condensation to develop on cooler surfaces. This can matter
            for windows, walls, pipes, equipment, buildings, and other
            temperature-sensitive surfaces.
          </p>

          <h2>Quick dew point guide</h2>

          <div className="tableWrap">
            <table>
              <thead>
                <tr>
                  <th>Dew Point</th>
                  <th>General Feel</th>
                </tr>
              </thead>

              <tbody>
                <tr>
                  <td>Below 50°F / 10°C</td>
                  <td>Comfortably dry</td>
                </tr>
                <tr>
                  <td>50–59°F / 10–15°C</td>
                  <td>Comfortable</td>
                </tr>
                <tr>
                  <td>60–64°F / 16–18°C</td>
                  <td>Slightly humid</td>
                </tr>
                <tr>
                  <td>65–69°F / 18–21°C</td>
                  <td>Humid</td>
                </tr>
                <tr>
                  <td>70°F+ / 21°C+</td>
                  <td>Very humid</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h2>Frequently asked questions</h2>

          <h3>Is dew point the same as humidity?</h3>

          <p>
            No. Relative humidity describes how saturated the air is relative
            to its current temperature, while dew point describes the
            temperature at which the air would become saturated.
          </p>

          <h3>What does a high dew point mean?</h3>

          <p>
            A higher dew point generally means there is more moisture in the
            air and conditions may feel more humid.
          </p>

          <h3>When does condensation occur?</h3>

          <p>
            Condensation can occur when a surface reaches or falls below the
            surrounding air's dew point.
          </p>
        </div>
      </section>

    <section className="content">
  <div className="container narrow">
    <h2>More AirPoint tools</h2>

    <p>
      Use our condensation calculator to compare surface temperature with
      dew point and estimate condensation risk.
    </p>

    <a href="/condensation-calculator" className="toolLink">
      Condensation Calculator →
    </a>
  </div>
</section>

<footer className="siteFooter">
  <div className="container footerGrid">
    <div className="footerBrand">
      <strong>AirPoint</strong>
      <span>Simple weather and moisture calculations.</span>
    </div>

    <div className="footerColumn">
      <h3>Tools</h3>
      <a href="/">Dew Point Calculator</a>
      <a href="/condensation-calculator">Condensation Calculator</a>
      <a href="/dew-point-chart">Dew Point Chart</a>
      <a href="/dew-point-vs-humidity">Dew Point vs. Humidity</a>
    </div>

    <div className="footerColumn">
      <h3>Learn</h3>
      <a href="/what-is-dew-point">What Is Dew Point?</a>
      <a href="/about">About AirPoint</a>
    </div>

    <div className="footerColumn">
      <h3>Information</h3>
      <a href="/privacy">Privacy Policy</a>
      <a href="/terms">Terms of Use</a>
      <a href="/contact">Contact</a>
    </div>
  </div>

  <div className="container footerBottom">
    <span>© 2026 AirPoint. All rights reserved.</span>
  </div>
</footer>
</main>
  );
}