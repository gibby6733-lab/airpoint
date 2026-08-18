"use client";

import { useState } from "react";

function calculateRelativeHumidity(tempC, dewPointC) {
  const a = 17.27;
  const b = 237.7;

  const gammaDewPoint =
    (a * dewPointC) / (b + dewPointC);

  const gammaTemperature =
    (a * tempC) / (b + tempC);

  const vaporPressureRatio =
    Math.exp(gammaDewPoint - gammaTemperature);

  return Math.max(
    0,
    Math.min(100, vaporPressureRatio * 100)
  );
}

function fToC(f) {
  return ((f - 32) * 5) / 9;
}

function getHumidityLevel(rh) {
  if (rh < 30) {
    return {
      label: "Dry",
      text: "The air contains relatively little moisture and may feel dry.",
    };
  }

  if (rh < 50) {
    return {
      label: "Comfortable",
      text: "Humidity is generally within a comfortable range for many indoor environments.",
    };
  }

  if (rh < 60) {
    return {
      label: "Moderate",
      text: "Humidity is moderately elevated but is still comfortable for many people.",
    };
  }

  if (rh < 70) {
    return {
      label: "Humid",
      text: "The air contains a noticeable amount of moisture and may feel humid.",
    };
  }

  return {
    label: "Very humid",
    text: "The air contains a high amount of moisture and may feel very humid.",
  };
}

export default function RelativeHumidityCalculator() {
  const [temperature, setTemperature] = useState("77");
  const [dewPoint, setDewPoint] = useState("59");
  const [unit, setUnit] = useState("F");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  function calculate() {
    const temp = Number(temperature);
    const dp = Number(dewPoint);

    if (!Number.isFinite(temp) || !Number.isFinite(dp)) {
      setError("Enter a valid temperature and dew point.");
      setResult(null);
      return;
    }

    const tempC = unit === "C" ? temp : fToC(temp);
    const dewPointC = unit === "C" ? dp : fToC(dp);

    if (dewPointC > tempC) {
      setError(
        "Dew point cannot be higher than the air temperature."
      );
      setResult(null);
      return;
    }

    const humidity = calculateRelativeHumidity(
      tempC,
      dewPointC
    );

    setError("");

    setResult({
      humidity,
      level: getHumidityLevel(humidity),
    });
  }

  return (
    <main className="site">
      <section className="hero">
        <div className="container">
          <div className="badge">AIRPOINT</div>

          <h1>Relative Humidity Calculator</h1>

          <p className="heroText">
            Calculate relative humidity from air temperature and
            dew point.
          </p>

          <div className="calculator">
            <div className="field">
              <label>Air Temperature</label>

              <div className="inputRow">
                <input
                  type="number"
                  value={temperature}
                  onChange={(e) =>
                    setTemperature(e.target.value)
                  }
                />

                <select
                  value={unit}
                  onChange={(e) =>
                    setUnit(e.target.value)
                  }
                >
                  <option value="F">°F</option>
                  <option value="C">°C</option>
                </select>
              </div>
            </div>

            <div className="field">
              <label>Dew Point</label>

              <div className="inputRow">
                <input
                  type="number"
                  value={dewPoint}
                  onChange={(e) =>
                    setDewPoint(e.target.value)
                  }
                />

                <span className="unit">
                  °{unit}
                </span>
              </div>
            </div>

            <button onClick={calculate}>
              Calculate Relative Humidity
            </button>

            {error && (
              <div className="risk">
                <strong>Check your inputs</strong>
                <p>{error}</p>
              </div>
            )}

            {result && (
              <div className="result">
                <span className="resultLabel">
                  RELATIVE HUMIDITY
                </span>

                <div className="resultNumber">
                  {result.humidity.toFixed(1)}%
                </div>

                <div className="risk">
                  <strong>
                    {result.level.label}
                  </strong>

                  <p>{result.level.text}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      <section className="content">
        <div className="container narrow">
          <h2>What is relative humidity?</h2>

          <p>
            Relative humidity is the amount of water vapor in
            the air compared with the maximum amount of moisture
            the air can hold at its current temperature.
          </p>

          <p>
            Relative humidity is expressed as a percentage.
            Higher percentages mean the air is closer to
            saturation.
          </p>

          <h2>How to calculate relative humidity</h2>

          <p>
            AirPoint calculates relative humidity using air
            temperature and dew point. The calculation uses the
            relationship between temperature, saturation vapor
            pressure, and actual vapor pressure.
          </p>

          <h2>Relative humidity and dew point</h2>

          <p>
            Dew point and relative humidity are closely related,
            but they are not the same measurement. Dew point is
            the temperature at which air becomes saturated, while
            relative humidity describes how close the air is to
            saturation at its current temperature.
          </p>

          <h2>Relative humidity guide</h2>

          <div className="tableWrap">
            <table>
              <thead>
                <tr>
                  <th>Relative Humidity</th>
                  <th>General Description</th>
                </tr>
              </thead>

              <tbody>
                <tr>
                  <td>Below 30%</td>
                  <td>Dry</td>
                </tr>

                <tr>
                  <td>30–49%</td>
                  <td>Comfortable</td>
                </tr>

                <tr>
                  <td>50–59%</td>
                  <td>Moderate</td>
                </tr>

                <tr>
                  <td>60–69%</td>
                  <td>Humid</td>
                </tr>

                <tr>
                  <td>70%+</td>
                  <td>Very humid</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h2>Frequently asked questions</h2>

          <h3>What is the difference between humidity and relative humidity?</h3>

          <p>
            Humidity generally refers to moisture in the air,
            while relative humidity compares the amount of
            moisture present with the amount the air can hold at
            its current temperature.
          </p>

          <h3>What is a comfortable relative humidity?</h3>

          <p>
            Many indoor environments are comfortable around
            30% to 60% relative humidity, although comfort varies
            depending on temperature and individual preference.
          </p>

          <h3>What happens when relative humidity reaches 100%?</h3>

          <p>
            At 100% relative humidity, the air is saturated.
            Additional cooling can cause water vapor to
            condense into liquid water.
          </p>

          <h3>Does temperature affect relative humidity?</h3>

          <p>
            Yes. Relative humidity can change when temperature
            changes even if the amount of water vapor in the air
            remains the same.
          </p>
        </div>
      </section>

      <footer>
        <div className="container">
          <strong>AirPoint</strong>
          <span>
            Simple weather and moisture calculations.
          </span>
        </div>
      </footer>
    </main>
  );
}