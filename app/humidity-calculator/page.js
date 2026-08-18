"use client";

import { useState } from "react";

function calculateRelativeHumidity(tempC, dewPointC) {
  const a = 17.27;
  const b = 237.7;

  const actual =
    Math.exp((a * dewPointC) / (b + dewPointC));

  const saturation =
    Math.exp((a * tempC) / (b + tempC));

  return Math.max(
    0,
    Math.min(100, 100 * (actual / saturation))
  );
}

function fToC(f) {
  return ((f - 32) * 5) / 9;
}

function getHumidityDescription(rh) {
  if (rh < 30) {
    return {
      label: "Dry",
      text: "The air contains relatively little moisture. Indoor air may feel dry.",
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

export default function HumidityCalculator() {
  const [temperature, setTemperature] = useState("25");
  const [dewPoint, setDewPoint] = useState("15");
  const [unit, setUnit] = useState("C");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  function calculate() {
    const temp = Number(temperature);
    const dp = Number(dewPoint);

    if (!Number.isFinite(temp) || !Number.isFinite(dp)) {
      setError("Enter valid temperature and dew point values.");
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

    const rh = calculateRelativeHumidity(tempC, dewPointC);

    setError("");
    setResult({
      rh,
      description: getHumidityDescription(rh),
    });
  }

  return (
    <main className="site">
      <section className="hero">
        <div className="container">
          <div className="badge">AIRPOINT</div>

          <h1>Humidity Calculator</h1>

          <p className="heroText">
            Calculate relative humidity from air temperature and dew point.
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
                  <option value="C">°C</option>
                  <option value="F">°F</option>
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
              Calculate Humidity
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
                  {result.rh.toFixed(1)}%
                </div>

                <div className="risk">
                  <strong>
                    {result.description.label}
                  </strong>

                  <p>
                    {result.description.text}
                  </p>
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
            Relative humidity describes how much water vapor is
            present in the air compared with the maximum amount
            the air could hold at its current temperature.
          </p>

          <p>
            Relative humidity is expressed as a percentage. A
            reading of 50% means the air contains roughly half
            of the moisture it could hold at that temperature.
          </p>

          <h2>How to calculate relative humidity</h2>

          <p>
            AirPoint estimates relative humidity using air
            temperature and dew point. Because warmer air can
            hold more water vapor, the same amount of moisture
            can produce different relative humidity values at
            different temperatures.
          </p>

          <h2>Humidity and dew point</h2>

          <p>
            Dew point and relative humidity describe moisture
            from different perspectives. Dew point is the
            temperature at which air becomes saturated, while
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

          <h3>Is relative humidity the same as dew point?</h3>

          <p>
            No. Relative humidity measures how close air is to
            saturation at its current temperature. Dew point is
            the temperature at which saturation would occur.
          </p>

          <h3>What is a comfortable humidity level?</h3>

          <p>
            Many indoor environments feel comfortable around
            30% to 60% relative humidity, although individual
            preferences and conditions vary.
          </p>

          <h3>Can relative humidity be over 100%?</h3>

          <p>
            Relative humidity is normally expressed as a
            percentage up to 100%. Values reaching saturation
            indicate that the air has reached its moisture
            capacity at that temperature.
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