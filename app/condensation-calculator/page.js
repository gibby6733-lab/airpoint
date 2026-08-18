"use client";

import { useState } from "react";
import Link from "next/link";

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

export default function CondensationCalculator() {
  const [temperature, setTemperature] = useState("25");
  const [humidity, setHumidity] = useState("60");
  const [surfaceTemperature, setSurfaceTemperature] = useState("18");
  const [result, setResult] = useState(null);

  function calculate() {
    const airTemp = Number(temperature);
    const rh = Number(humidity);
    const surfaceTemp = Number(surfaceTemperature);

    if (
      !Number.isFinite(airTemp) ||
      !Number.isFinite(rh) ||
      !Number.isFinite(surfaceTemp) ||
      rh <= 0 ||
      rh > 100
    ) {
      setResult({
        error: "Enter a valid temperature, surface temperature, and humidity between 1% and 100%.",
      });
      return;
    }

    const dewPoint = calculateDewPoint(airTemp, rh);
    const difference = surfaceTemp - dewPoint;

    let risk;
    let message;

    if (surfaceTemp <= dewPoint) {
      risk = "Condensation likely";
      message =
        "The surface temperature is at or below the dew point. Water vapor can condense on the surface.";
    } else if (difference <= 2) {
      risk = "High risk";
      message =
        "The surface is very close to the dew point. A small temperature drop could cause condensation.";
    } else if (difference <= 5) {
      risk = "Moderate risk";
      message =
        "The surface is above the dew point, but there is a noticeable moisture risk if conditions change.";
    } else {
      risk = "Low risk";
      message =
        "The surface is comfortably above the dew point, so condensation is less likely under these conditions.";
    }

    setResult({
      dewPoint,
      difference,
      risk,
      message,
    });
  }

  return (
    <main className="site">
      <section className="hero">
        <div className="container">
          <div className="badge">AIRPOINT TOOL</div>

          <h1>Condensation Calculator</h1>

          <p className="heroText">
            Find the dew point and estimate whether condensation is likely to
            form on a surface.
          </p>

          <Link href="/" className="backLink">
            ← Dew Point Calculator
          </Link>
        </div>
      </section>

      <section className="content">
        <div className="container narrow">
          <div className="calculatorCard">
            <h2>Check condensation risk</h2>

            <div className="formGroup">
              <label htmlFor="temperature">Air temperature (°C)</label>
              <input
                id="temperature"
                type="number"
                value={temperature}
                onChange={(e) => setTemperature(e.target.value)}
              />
            </div>

            <div className="formGroup">
              <label htmlFor="humidity">Relative humidity (%)</label>
              <input
                id="humidity"
                type="number"
                min="1"
                max="100"
                value={humidity}
                onChange={(e) => setHumidity(e.target.value)}
              />
            </div>

            <div className="formGroup">
              <label htmlFor="surfaceTemperature">
                Surface temperature (°C)
              </label>
              <input
                id="surfaceTemperature"
                type="number"
                value={surfaceTemperature}
                onChange={(e) => setSurfaceTemperature(e.target.value)}
              />
            </div>

            <button onClick={calculate} className="primaryButton">
              Calculate Condensation Risk
            </button>

            {result?.error && (
              <div className="infoCard">
                <strong>Check your inputs</strong>
                <p>{result.error}</p>
              </div>
            )}

            {result && !result.error && (
              <div className="infoCard">
                <strong>{result.risk}</strong>

                <p>{result.message}</p>

                <p>
                  <strong>Dew point:</strong>{" "}
                  {result.dewPoint.toFixed(1)}°C (
                  {cToF(result.dewPoint).toFixed(1)}°F)
                </p>

                <p>
                  <strong>Surface vs. dew point:</strong>{" "}
                  {result.difference.toFixed(1)}°C
                </p>
              </div>
            )}
          </div>

          <h2>How the condensation calculator works</h2>

          <p>
            Condensation occurs when a surface becomes cold enough for the
            surrounding air to reach its dew point. AirPoint first calculates
            the dew point using the air temperature and relative humidity.
          </p>

          <p>
            It then compares the surface temperature with the calculated dew
            point. If the surface reaches or falls below the dew point,
            condensation is likely to occur.
          </p>

          <h2>Why condensation happens</h2>

          <p>
            Warm air can hold more water vapor than cold air. When moist air
            comes into contact with a colder surface, the air immediately
            around that surface can cool to its dew point. When saturation is
            reached, water vapor can turn into liquid water.
          </p>

          <h2>Common examples</h2>

          <ul className="linkList">
            <li>Water forming on cold windows</li>
            <li>Moisture appearing on pipes</li>
            <li>Condensation on vehicles</li>
            <li>Moisture on air-conditioning equipment</li>
            <li>Humidity-related building problems</li>
          </ul>

          <h2>Important note</h2>

          <p>
            This calculator provides an estimate based on air temperature,
            relative humidity, and surface temperature. Actual condensation
            can also depend on airflow, surface properties, temperature
            gradients, and local conditions.
          </p>

          <h2>More AirPoint tools</h2>

          <ul className="linkList">
            <li>
              <Link href="/">Dew Point Calculator</Link>
            </li>
            <li>
              <Link href="/dew-point-chart">Dew Point Chart</Link>
            </li>
            <li>
              <Link href="/what-is-dew-point">What Is Dew Point?</Link>
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