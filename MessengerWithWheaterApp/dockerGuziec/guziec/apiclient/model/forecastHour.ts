import { Main } from "./main";
import { Weather } from "./Weather";
import { Clouds } from "./Clouds";
import { Wind } from "./wind";
import { H3 } from "./h3";
import { System } from "./system";


export interface ForecastHour { 
    /**
     * Unix Timestamp
     */
    dt?: string;
    /**
     * Timestamp in local time
     */
    main?: Main;
    /**
     * Timestamp UTC
     */
    weather?: Array<Weather>;
    /**
     * Date in format \"YYYY-MM-DD:HH\". All datetime is in (UTC)
     */
    clouds?: Clouds;
    /**
     * Accumulated snowfall since last forecast point - Default (mm)
     */
    wind?: Wind;
    /**
     * Snow depth - Default (mm)
     */
    visibility?: number;
    /**
     * 6 hour accumulated snowfall. Default (mm)
     */
    pop?: number;
    /**
     * Accumulated precipitation since last forecast point. Default (mm)
     */
    rain?: H3;
    /**
     * Temperature - Default (C)
     */
    sys?: System;
    /**
     * Dewpoint - Default (C)
     */
    dt_txt?: string;
}

