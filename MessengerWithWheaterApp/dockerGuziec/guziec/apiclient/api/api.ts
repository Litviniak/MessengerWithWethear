export * from './default.service';
import { DefaultService } from './default.service';
export * from './class120HourHourlyForecast.service';
import { Class120HourHourlyForecastService } from './class120HourHourlyForecast.service';
export * from './class120HourHourlyForecast.serviceInterface'
export * from './class16DayDailyForecast.service';
import { Class16DayDailyForecastService } from './class16DayDailyForecast.service';
export * from './class16DayDailyForecast.serviceInterface'
export const APIS = [DefaultService,Class120HourHourlyForecastService, Class16DayDailyForecastService];
