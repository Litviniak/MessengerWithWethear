import { Observable } from 'rxjs';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class WebsocketService {
  ws: WebSocket;
  socketIsOpen = 1;
  createObservableSocket(url:string): Observable<any>{
    this.ws = new WebSocket(url);

    return new Observable(
      observer => {
        this.ws.onmessage  = (event) => observer.next(event.data);

        this.ws.onerror = (event) => observer.error(event);

        this.ws.onclose = (event) => observer.complete();

        return () => this.ws.close()
      }
    );
  }
}
