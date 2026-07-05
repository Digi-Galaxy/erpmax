package worker

import (
	"log"
	"sync"

	"erpmax-go/internal/services"
)

type Pool struct {
	workers   int
	jobChan   chan *services.Job
	done      chan struct{}
	wg        sync.WaitGroup
	jobService *services.JobService
}

func NewPool(workers int, jobService *services.JobService) *Pool {
	return &Pool{
		workers:    workers,
		jobChan:    make(chan *services.Job, 100),
		done:       make(chan struct{}),
		jobService: jobService,
	}
}

func (p *Pool) Start() {
	for i := 0; i < p.workers; i++ {
		p.wg.Add(1)
		go p.worker(i)
	}
	log.Printf("Started %d workers", p.workers)
}

func (p *Pool) Stop() {
	close(p.done)
	p.wg.Wait()
	log.Println("All workers stopped")
}

func (p *Pool) worker(id int) {
	defer p.wg.Done()

	for {
		select {
		case <-p.done:
			return
		case job := <-p.jobChan:
			log.Printf("Worker %d processing job %s", id, job.ID)
			p.jobService.ProcessJob(job)
		}
	}
}

func (p *Pool) Submit(job *services.Job) {
	p.jobChan <- job
}
