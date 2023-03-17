<?php
require 'Request.php';
class Curl {
    private $simultaneousLimit = 5;
    private $callback;
    private $idleCallback;
    protected $options = array(CURLOPT_RETURNTRANSFER => 1, CURLOPT_FOLLOWLOCATION => 1, CURLOPT_MAXREDIRS => 5, CURLOPT_CONNECTTIMEOUT => 30, CURLOPT_TIMEOUT => 30);
    protected $multicurlOptions = array();
    private $headers = array();
    private $pendingRequests = array();
    private $pendingRequestsPosition = 0;
    private $activeRequests = array();
    private $completedRequests = array();
    private $completedRequestCount = 0;
    public function add(Request $request) {
        $this->pendingRequests[] = $request;
        return $this;
    }
    public function request($url, $method = "GET", $postData = null, $headers = null, $options = null) {
        $newRequest = new Request($url, $method);
        if ($postData) {
            $newRequest->setPostData($postData);
        }
        if ($headers) {
            $newRequest->setHeaders($headers);
        }
        if ($options) {
            $newRequest->setOptions($options);
        }
        return $this->add($newRequest);
    }
    public function get($url, $headers = null, $options = null) {
        return $this->request($url, "GET", null, $headers, $options);
    }
    public function post($url, $postData = null, $headers = null, $options = null) {
        return $this->request($url, "POST", $postData, $headers, $options);
    }
    public function put($url, $putData = null, $headers = null, $options = null) {
        return $this->request($url, "PUT", $putData, $headers, $options);
    }
    public function delete($url, $headers = null, $options = null) {
        return $this->request($url, "DELETE", null, $headers, $options);
    }
    public function execute() {
        $master = curl_multi_init();
        foreach ($this->multicurlOptions AS $multiOption => $multiValue) {
            curl_multi_setopt($master, $multiOption, $multiValue);
        }
        $firstBatch = $this->getNextPendingRequests($this->getSimultaneousLimit());
        if (count($firstBatch) == 0) {
            return;
        }
        foreach ($firstBatch as $request) {
            $ch      = curl_init();
            $options = $this->prepareRequestOptions($request);
            curl_setopt_array($ch, $options);
            curl_multi_add_handle($master, $ch);
            $this->activeRequests[(int) $ch] = $request;
        }
        $active        = null;
        $idleCallback  = $this->idleCallback;
        $selectTimeout = $idleCallback ? 0.1 : 1.0;
        do {
            $status = curl_multi_exec($master, $active);
            while ($transfer = curl_multi_info_read($master)) {
                $key     = (int) $transfer['handle'];
                $request = $this->activeRequests[$key];
                $request->setResponseText(curl_multi_getcontent($transfer['handle']));
                $request->setResponseErrno(curl_errno($transfer['handle']));
                $request->setResponseError(curl_error($transfer['handle']));
                $request->setResponseInfo(curl_getinfo($transfer['handle']));
                unset($this->activeRequests[$key]);
                $this->completedRequests[] = $request;
                $this->completedRequestCount++;
                if ($nextRequest = $this->getNextPendingRequest()) {
                    $ch      = curl_init();
                    $options = $this->prepareRequestOptions($nextRequest);
                    curl_setopt_array($ch, $options);
                    curl_multi_add_handle($master, $ch);
                    $this->activeRequests[(int) $ch] = $nextRequest;
                }
                curl_multi_remove_handle($master, $transfer['handle']);
                if (is_callable($this->callback)) {
                    $callback = $this->callback;
                    $callback($request, $this);
                }
                $status = curl_multi_exec($master, $active);
            }
            $err = null;
            switch ($status) {
                case CURLM_BAD_EASY_HANDLE:
                    $err = 'CURLM_BAD_EASY_HANDLE';
                    break;
                case CURLM_OUT_OF_MEMORY:
                    $err = 'CURLM_OUT_OF_MEMORY';
                    break;
                case CURLM_INTERNAL_ERROR:
                    $err = 'CURLM_INTERNAL_ERROR';
                    break;
                case CURLM_BAD_HANDLE:
                    $err = 'CURLM_BAD_HANDLE';
                    break;
            }
            if ($err) {
                throw new \Exception("curl_multi_exec failed with error code ($status) const ($err)");
            }
            while (0 == curl_multi_select($master, $selectTimeout) && $idleCallback) {
                $idleCallback($this);
            }
        } while ($status === CURLM_CALL_MULTI_PERFORM || $active);
        curl_multi_close($master);
    }
    private function prepareRequestOptions(Request $request) {
        $options                        = $this->getOptions();
        $options[CURLOPT_URL]           = $request->getUrl();
        $options[CURLOPT_CUSTOMREQUEST] = $request->getMethod();
        if ($request->getPostData()) {
            $options[CURLOPT_POST]       = 1;
            $options[CURLOPT_POSTFIELDS] = $request->getPostData();
        }
        if ($request->getHeaders()) {
            $options[CURLOPT_HEADER]     = 0;
            $options[CURLOPT_HTTPHEADER] = $request->getHeaders();
        } elseif ($this->getHeaders()) {
            $options[CURLOPT_HEADER]     = 0;
            $options[CURLOPT_HTTPHEADER] = $this->getHeaders();
        }
        if ($request->getOptions()) {
            $options = $request->getOptions() + $options;
        }
        return $options;
    }
    public function setCallback($callback) {
        if (!is_callable($callback)) {
            throw new \InvalidArgumentException("must pass in a callable instance");
        }
        $this->callback = $callback;
        return $this;
    }
    public function getCallback() {
        return $this->callback;
    }
    public function setIdleCallback(callable $callback) {
        $this->idleCallback = $callback;
        return $this;
    }
    public function getIdleCallback() {
        return $this->idleCallback;
    }
    public function setHeaders($headers) {
        if (!is_array($headers)) {
            throw new \InvalidArgumentException("headers must be an array");
        }
        $this->headers = $headers;
        return $this;
    }
    public function getHeaders() {
        return $this->headers;
    }
    public function setOptions($options) {
        if (!is_array($options)) {
            throw new \InvalidArgumentException("options must be an array");
        }
        $this->options = $options;
        return $this;
    }
    public function addOptions($options) {
        if (!is_array($options)) {
            throw new \InvalidArgumentException("options must be an array");
        }
        $this->options = $options + $this->options;
        return $this;
    }
    public function getOptions() {
        return $this->options;
    }
    public function setMulticurlOptions($multicurlOptions) {
        if (!is_array($multicurlOptions)) {
            throw new \InvalidArgumentException("multicurlOptions must be an array");
        }
        $this->multicurlOptions = $multicurlOptions;
        return $this;
    }
    public function addMulticurlOptions($multicurlOptions) {
        if (!is_array($multicurlOptions)) {
            throw new \InvalidArgumentException("multicurlOptions must be an array");
        }
        $this->multicurlOptions = $multicurlOptions + $this->multicurlOptions;
        return $this;
    }
    public function getMulticurlOptions() {
        return $this->multicurlOptions;
    }
    public function setSimultaneousLimit($count) {
        if (!is_int($count) || $count < 2) {
            throw new \InvalidArgumentException("setSimultaneousLimit count must be an int >= 2");
        }
        $this->simultaneousLimit = $count;
        return $this;
    }
    public function getSimultaneousLimit() {
        return $this->simultaneousLimit;
    }
    public function getCompletedRequests() {
        return $this->completedRequests;
    }
    private function getNextPendingRequests($limit = 1) {
        $requests = array();
        while ($limit--) {
            if (!isset($this->pendingRequests[$this->pendingRequestsPosition])) {
                break;
            }
            $requests[] = $this->pendingRequests[$this->pendingRequestsPosition];
            $this->pendingRequestsPosition++;
        }
        return $requests;
    }
    private function getNextPendingRequest() {
        $next = $this->getNextPendingRequests();
        return count($next) ? $next[0] : null;
    }
    public function prunePendingRequestQueue() {
        $this->pendingRequests         = $this->getNextPendingRequests(0);
        $this->pendingRequestsPosition = 0;
        return $this;
    }
    public function countCompleted($useArray = false) {
        return $useArray ? count($this->completedRequests) : $this->completedRequestCount;
    }
    public function countPending() {
        return count($this->pendingRequests) - $this->pendingRequestsPosition;
    }
    public function countActive() {
        return count($this->activeRequests);
    }
    public function clearCompleted() {
        $this->completedRequests = array();
        gc_collect_cycles();
        return $this;
    }
}